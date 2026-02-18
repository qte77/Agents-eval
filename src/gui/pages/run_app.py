"""
Streamlit interface for running the agentic system interactively.

This module defines the render_app function, which provides a Streamlit-based UI
for users to select a provider, enter a query, and execute the main agent workflow.
Results and errors are displayed in real time, supporting asynchronous execution.

Provider and sub-agent configuration are read from session state, allowing users
to configure these settings on the Settings page before running queries.

Background execution support allows queries to continue running even when users
navigate to other tabs, with results persisted in session state.

Input mode supports both free-form text queries and paper selection from
downloaded PeerRead papers via a dropdown with abstract preview.
"""

import shutil
from pathlib import Path

import streamlit as st
from streamlit import button, exception, header, info, spinner, subheader, text_input, warning

from app.app import main
from app.common.settings import CommonSettings
from app.config.config_app import CHAT_DEFAULT_PROVIDER
from app.data_models.peerread_models import PeerReadPaper
from app.data_utils.datasets_peerread import PeerReadLoader
from app.judge.settings import JudgeSettings
from app.utils.log import logger
from gui.components.output import render_output
from gui.config.text import (
    OUTPUT_SUBHEADER,
    RUN_APP_BUTTON,
    RUN_APP_HEADER,
    RUN_APP_OUTPUT_PLACEHOLDER,
    RUN_APP_QUERY_PLACEHOLDER,
    RUN_APP_QUERY_RUN_INFO,
    RUN_APP_QUERY_WARNING,
)
from gui.utils.log_capture import LogCapture


def _collect_unique_papers(
    loader: PeerReadLoader,
    venue: str,
    split: str,
    seen_ids: set[str],
    papers: list[PeerReadPaper],
) -> None:
    """Collect unique papers from a single venue/split combination.

    Appends papers not already in seen_ids. Silently skips when the
    venue/split data has not been downloaded (FileNotFoundError).

    Args:
        loader: PeerReadLoader instance to load papers from.
        venue: Venue name (e.g. "acl_2017").
        split: Data split name (e.g. "train").
        seen_ids: Mutable set tracking already-collected paper IDs.
        papers: Mutable list to append new papers to.
    """
    try:
        for paper in loader.load_papers(venue, split):
            if paper.paper_id not in seen_ids:
                seen_ids.add(paper.paper_id)
                papers.append(paper)
    except FileNotFoundError:
        pass


def _load_available_papers() -> list[PeerReadPaper]:
    """Load all locally downloaded PeerRead papers across configured venues and splits.

    Iterates all configured venues and splits, collecting unique papers by paper_id.
    Returns an empty list when the dataset has not been downloaded yet.

    Returns:
        Deduplicated list of PeerReadPaper objects available locally.
    """
    loader = PeerReadLoader()
    seen_ids: set[str] = set()
    papers: list[PeerReadPaper] = []

    for venue in loader.config.venues:
        for split in loader.config.splits:
            _collect_unique_papers(loader, venue, split, seen_ids, papers)

    return papers


def _format_paper_option(paper: PeerReadPaper) -> str:
    """Format a PeerReadPaper as a dropdown display string.

    Args:
        paper: PeerReadPaper to format.

    Returns:
        String in the form "<paper_id> \u2014 <title>".
    """
    return f"{paper.paper_id} \u2014 {paper.title}"


def _get_session_config(provider: str | None) -> tuple[str, bool, bool, bool]:
    """Extract configuration from session state.

    Args:
        provider: Optional provider override

    Returns:
        Tuple of (provider, include_researcher, include_analyst, include_synthesiser)
    """
    provider_from_state: str = st.session_state.get(
        "chat_provider", provider or CHAT_DEFAULT_PROVIDER
    )
    include_researcher: bool = st.session_state.get("include_researcher", False)
    include_analyst: bool = st.session_state.get("include_analyst", False)
    include_synthesiser: bool = st.session_state.get("include_synthesiser", False)
    return provider_from_state, include_researcher, include_analyst, include_synthesiser


def _build_judge_settings_from_session() -> JudgeSettings | None:
    """Build JudgeSettings from session state overrides.

    Checks session state for judge settings overrides (prefixed with 'judge_')
    and constructs a JudgeSettings instance if any are found. If no overrides
    exist, returns None to use defaults.

    Returns:
        JudgeSettings instance with session state overrides, or None if no overrides.
    """
    # Check if any judge settings exist in session state
    judge_overrides = {
        k.replace("judge_", ""): v
        for k, v in st.session_state.items()
        if isinstance(k, str) and k.startswith("judge_")
    }

    if not judge_overrides:
        return None

    # Build JudgeSettings with overrides
    return JudgeSettings(**judge_overrides)


def _build_common_settings_from_session() -> CommonSettings | None:
    """Build CommonSettings from session state overrides.

    Checks session state for common settings overrides (prefixed with 'common_')
    and constructs a CommonSettings instance if any are found. If no overrides
    exist, returns None to use defaults.

    Returns:
        CommonSettings instance with session state overrides, or None if no overrides.
    """
    common_overrides = {
        k.replace("common_", ""): v
        for k, v in st.session_state.items()
        if isinstance(k, str) and k.startswith("common_")
    }

    if not common_overrides:
        return None

    return CommonSettings(**common_overrides)


def _format_enabled_agents(
    include_researcher: bool, include_analyst: bool, include_synthesiser: bool
) -> str:
    """Format list of enabled agents for display.

    Args:
        include_researcher: Whether researcher is enabled
        include_analyst: Whether analyst is enabled
        include_synthesiser: Whether synthesiser is enabled

    Returns:
        Formatted string of enabled agents
    """
    enabled_agents: list[str] = []
    if include_researcher:
        enabled_agents.append("Researcher")
    if include_analyst:
        enabled_agents.append("Analyst")
    if include_synthesiser:
        enabled_agents.append("Synthesiser")
    return ", ".join(enabled_agents) if enabled_agents else "None (Manager only)"


def _initialize_execution_state() -> None:
    """Initialize execution state in session state if not already set."""
    if not hasattr(st.session_state, "execution_state"):
        st.session_state.execution_state = "idle"


def _get_execution_state() -> str:
    """Get current execution state from session state.

    Returns:
        Current execution state: 'idle', 'running', 'completed', or 'error'
    """
    return getattr(st.session_state, "execution_state", "idle")


def _capture_execution_logs(capture: LogCapture) -> None:
    """Capture logs during execution and store in session state.

    Args:
        capture: LogCapture instance to retrieve logs from
    """
    logs = capture.get_logs()
    st.session_state.debug_logs = logs


def _render_debug_log_panel() -> None:
    """Render the debug log panel with captured logs.

    Displays an expandable panel at the bottom of the App tab showing
    log entries captured during execution. Logs are color-coded by level.
    """
    logs = getattr(st.session_state, "debug_logs", [])

    with st.expander("Debug Log", expanded=False):
        if not logs:
            st.info("No logs captured yet. Run a query to see execution logs.")
        else:
            # Render logs as HTML with color coding
            html = LogCapture.format_logs_as_html(logs)
            st.markdown(html, unsafe_allow_html=True)


async def _execute_query_background(
    query: str,
    provider: str,
    include_researcher: bool,
    include_analyst: bool,
    include_synthesiser: bool,
    chat_config_file: str | Path | None,
    token_limit: int | None = None,
    judge_settings: JudgeSettings | None = None,
    paper_id: str | None = None,
    common_settings: CommonSettings | None = None,
    engine: str = "mas",
) -> None:
    """Execute agent query in background with session state persistence.

    Sets execution_state to 'running', executes query, then transitions to
    'completed' or 'error' based on outcome. Result/error stored in session state.

    Args:
        query: User query string
        provider: LLM provider name
        include_researcher: Whether to include researcher agent
        include_analyst: Whether to include analyst agent
        include_synthesiser: Whether to include synthesiser agent
        chat_config_file: Path to chat configuration file
        token_limit: Optional token limit override from GUI
        judge_settings: Optional JudgeSettings override from GUI settings page
        paper_id: Optional PeerRead paper ID for paper selection mode
        common_settings: Optional CommonSettings override from GUI settings page
        engine: Execution engine — 'mas' (PydanticAI) or 'cc' (Claude Code)
    """
    # Set running state
    st.session_state.execution_state = "running"
    st.session_state.execution_query = query
    st.session_state.execution_provider = provider

    # Setup log capture
    capture = LogCapture()
    handler_id = capture.attach_to_logger()

    try:
        # Execute query
        result = await main(
            chat_provider=provider,
            query=query,
            include_researcher=include_researcher,
            include_analyst=include_analyst,
            include_synthesiser=include_synthesiser,
            chat_config_file=chat_config_file,
            token_limit=token_limit,
            judge_settings=judge_settings,
            paper_id=paper_id,
            engine=engine,
        )

        # Store result and transition to completed
        st.session_state.execution_state = "completed"

        # Extract CompositeResult and graph from result dict
        if result is not None:
            st.session_state.execution_composite_result = result.get("composite_result")
            st.session_state.execution_graph = result.get("graph")
            # Keep legacy execution_result for backward compatibility
            st.session_state.execution_result = result.get("composite_result")
            # S8-F8.2: store execution_id for Evaluation Results page display
            st.session_state["execution_id"] = result.get("execution_id")
        else:
            # No evaluation result (e.g., skip_eval=True)
            st.session_state.execution_composite_result = None
            st.session_state.execution_graph = None
            st.session_state.execution_result = None
            st.session_state["execution_id"] = None

        # Clear error if previously set
        if hasattr(st.session_state, "execution_error"):
            delattr(st.session_state, "execution_error")

    except Exception as e:
        # Store error and transition to error state
        st.session_state.execution_state = "error"
        st.session_state.execution_error = str(e)

        # Clear result if previously set
        if hasattr(st.session_state, "execution_result"):
            delattr(st.session_state, "execution_result")

        logger.exception(e)

    finally:
        # Capture and store logs
        _capture_execution_logs(capture)
        capture.detach_from_logger(handler_id)


def _display_configuration(provider: str, token_limit: int | None, agents_text: str) -> None:
    """Display current provider and agent configuration.

    Args:
        provider: Active LLM provider
        token_limit: Optional token limit
        agents_text: Formatted string of enabled agents
    """
    st.markdown(f"**Provider:** {provider}")
    st.markdown(f"**Enabled Sub-Agents:** {agents_text}")
    if token_limit is not None:
        st.markdown(f"**Token Limit:** {token_limit}")


def _display_execution_result(execution_state: str) -> None:
    """Display execution result based on current state.

    Wraps state transitions in ARIA live regions for screen reader accessibility:
    - role="status" for running/completed (polite, non-interrupting)
    - role="alert" for errors (assertive, immediate announcement)

    Args:
        execution_state: Current execution state (running/completed/error/idle)
    """
    if execution_state == "running":
        # S8-F3.3: ARIA role="status" for polite announcement (WCAG 4.1.3)
        st.markdown('<div role="status" aria-live="polite">', unsafe_allow_html=True)
        with spinner("Query execution in progress..."):
            info(
                "Execution is running. You can navigate to other tabs and return to see the result."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    elif execution_state == "completed":
        result = getattr(st.session_state, "execution_result", None)
        # S8-F3.3: ARIA role="status" for completed state + post-run navigation guidance
        st.markdown('<div role="status" aria-live="polite">', unsafe_allow_html=True)
        if result:
            render_output(result)
        else:
            info("Execution completed but no result was returned.")
        st.markdown(
            "Navigate to **Evaluation Results** to view scores, "
            "or **Agent Graph** to explore agent interactions.",
            unsafe_allow_html=False,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    elif execution_state == "error":
        # S8-F3.3: ARIA role="alert" for error state (assertive announcement, WCAG 4.1.3)
        st.markdown('<div role="alert" aria-live="assertive">', unsafe_allow_html=True)
        error_msg = getattr(st.session_state, "execution_error", "Unknown error")
        exception(Exception(error_msg))
        st.markdown("</div>", unsafe_allow_html=True)

    else:  # idle
        render_output(RUN_APP_OUTPUT_PLACEHOLDER)


def _render_paper_selection_input() -> tuple[str, str | None]:
    """Render paper selection UI and return the user's query and selected paper ID.

    Loads available papers from session state (or fetches on first render),
    then renders a selectbox with abstract preview. Falls back to free-form
    text input when no papers are downloaded.

    Returns:
        Tuple of (query, selected_paper_id). selected_paper_id is None when
        no paper is selected or papers are unavailable.
    """
    available_papers: list[PeerReadPaper] = st.session_state.get("available_papers", [])
    if not available_papers:
        available_papers = _load_available_papers()
        st.session_state.available_papers = available_papers

    if not available_papers:
        # S8-F3.3: fix dead "Downloads page" reference — provide CLI instructions instead
        st.info(
            "No papers downloaded yet. "
            "Run `make setup_dataset_sample` in your terminal to fetch the PeerRead dataset."
        )
        return text_input(RUN_APP_QUERY_PLACEHOLDER), None

    selected_paper: PeerReadPaper = st.selectbox(
        "Select a paper",
        options=available_papers,
        format_func=_format_paper_option,
        key="selected_paper",
        help="Choose a PeerRead paper to evaluate. The abstract preview appears below.",
    )
    selected_paper_id = selected_paper.paper_id if selected_paper else None

    if selected_paper and selected_paper.abstract:
        st.markdown(f"> {selected_paper.abstract}")

    query = text_input(
        "Custom query (optional — leave blank to use default review template)",
        key="paper_mode_query",
    )
    return query, selected_paper_id


async def _handle_query_submission(
    query: str,
    selected_paper_id: str | None,
    provider: str,
    include_researcher: bool,
    include_analyst: bool,
    include_synthesiser: bool,
    chat_config_file: str | Path | None,
    token_limit: int | None,
    engine: str = "mas",
) -> None:
    """Validate input and execute the agent query in background.

    Does nothing when both query and selected_paper_id are empty (shows warning).
    Otherwise builds judge settings from session state, starts background execution,
    and triggers a Streamlit rerun to reflect updated state.

    Args:
        query: User query string (may be empty).
        selected_paper_id: Selected PeerRead paper ID, or None.
        provider: LLM provider name.
        include_researcher: Whether to include researcher agent.
        include_analyst: Whether to include analyst agent.
        include_synthesiser: Whether to include synthesiser agent.
        chat_config_file: Path to chat configuration file.
        token_limit: Optional token limit override from GUI.
        engine: Execution engine — 'mas' (PydanticAI) or 'cc' (Claude Code).
    """
    if not (query or selected_paper_id):
        warning(RUN_APP_QUERY_WARNING)
        return

    judge_settings = _build_judge_settings_from_session()
    common_settings = _build_common_settings_from_session()
    info(f"{RUN_APP_QUERY_RUN_INFO} {query or f'paper {selected_paper_id}'}")
    await _execute_query_background(
        query,
        provider,
        include_researcher,
        include_analyst,
        include_synthesiser,
        chat_config_file,
        token_limit,
        judge_settings,
        paper_id=selected_paper_id,
        common_settings=common_settings,
        engine=engine,
    )
    st.rerun()


async def render_app(provider: str | None = None, chat_config_file: str | Path | None = None):
    """Render the main app interface for running agentic queries via Streamlit.

    Displays input fields for provider and query, a button to trigger execution,
    and an area for output or error messages. Handles async invocation of the
    main agent workflow and logs any exceptions.

    Provider and sub-agent configuration are read from session state (configured
    on the Settings page). Execution runs in background with results persisted
    to session state, allowing navigation across tabs without losing progress.

    Engine selection (MAS or Claude Code) is per-run via a radio widget and
    stored in session state. When CC is selected, MAS-specific controls are
    disabled and CC availability is checked.
    """
    header(RUN_APP_HEADER)
    _initialize_execution_state()

    # CC availability: compute once and cache in session state
    st.session_state.setdefault("cc_available", shutil.which("claude") is not None)
    cc_available: bool = st.session_state.cc_available

    provider_from_state, include_researcher, include_analyst, include_synthesiser = (
        _get_session_config(provider)
    )
    token_limit: int | None = st.session_state.get("token_limit")

    # Engine selector — per-run choice, not persistent config
    engine_label = st.radio(
        "Execution engine",
        ["MAS (PydanticAI)", "Claude Code"],
        key="engine_label",
        horizontal=True,
        # S8-F3.3: help text for engine selector
        help=(
            "MAS (PydanticAI): multi-agent pipeline with Researcher, Analyst, and Synthesiser. "
            "Claude Code: single-model execution via the `claude` CLI."
        ),
    )
    engine = "cc" if engine_label == "Claude Code" else "mas"
    st.session_state.engine = engine

    if engine == "cc" and not cc_available:
        st.warning(
            "Claude Code CLI (`claude`) not found on PATH. "
            "Install it to use the CC engine: https://docs.anthropic.com/en/docs/claude-code"
        )

    if engine == "cc":
        # S8-F8.2: hide MAS controls entirely when CC engine selected (not just disabled)
        st.info(
            "MAS agent controls (Researcher, Analyst, Synthesiser) are not applicable "
            "when using the Claude Code engine."
        )
    else:
        agents_text = _format_enabled_agents(include_researcher, include_analyst, include_synthesiser)
        _display_configuration(provider_from_state, token_limit, agents_text)

    input_mode = st.radio(
        "Input mode",
        ["Free-form query", "Select a paper"],
        key="input_mode",
        horizontal=True,
    )

    if input_mode == "Free-form query":
        query = text_input(RUN_APP_QUERY_PLACEHOLDER)
        selected_paper_id: str | None = None
    else:
        query, selected_paper_id = _render_paper_selection_input()

    if button(RUN_APP_BUTTON):
        await _handle_query_submission(
            query,
            selected_paper_id,
            provider_from_state,
            include_researcher,
            include_analyst,
            include_synthesiser,
            chat_config_file,
            token_limit,
            engine=engine,
        )

    # S8-F8.1: subheader placed after run button so output section follows user action
    subheader(OUTPUT_SUBHEADER)
    _display_execution_result(_get_execution_state())
    _render_debug_log_panel()
