"""
Streamlit interface for running the agentic system interactively.

This module defines the render_app function, which provides a Streamlit-based UI
for users to select a provider, enter a query, and execute the main agent workflow.
Results and errors are displayed in real time, supporting asynchronous execution.

Provider and sub-agent configuration are read from session state, allowing users
to configure these settings on the Settings page before running queries.

Background execution support allows queries to continue running even when users
navigate to other tabs, with results persisted in session state.
"""

from pathlib import Path

import streamlit as st
from streamlit import button, exception, header, info, spinner, subheader, text, text_input, warning

from app.app import main
from app.config.config_app import CHAT_DEFAULT_PROVIDER
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
        )

        # Store result and transition to completed
        st.session_state.execution_state = "completed"
        st.session_state.execution_result = result

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
    text(f"**Provider:** {provider}")
    text(f"**Enabled Sub-Agents:** {agents_text}")
    if token_limit is not None:
        text(f"**Token Limit:** {token_limit}")


def _display_execution_result(execution_state: str) -> None:
    """Display execution result based on current state.

    Args:
        execution_state: Current execution state (running/completed/error/idle)
    """
    if execution_state == "running":
        with spinner("Query execution in progress..."):
            info(
                "Execution is running. You can navigate to other tabs and return to see the result."
            )

    elif execution_state == "completed":
        result = getattr(st.session_state, "execution_result", None)
        if result:
            render_output(result)
        else:
            info("Execution completed but no result was returned.")

    elif execution_state == "error":
        error_msg = getattr(st.session_state, "execution_error", "Unknown error")
        exception(Exception(error_msg))

    else:  # idle
        render_output(RUN_APP_OUTPUT_PLACEHOLDER)


async def render_app(provider: str | None = None, chat_config_file: str | Path | None = None):
    """
    Render the main app interface for running agentic queries via Streamlit.

    Displays input fields for provider and query, a button to trigger execution,
    and an area for output or error messages. Handles async invocation of the
    main agent workflow and logs any exceptions.

    Provider and sub-agent configuration are read from session state (configured
    on the Settings page). Execution runs in background with results persisted
    to session state, allowing navigation across tabs without losing progress.
    """
    header(RUN_APP_HEADER)

    # Initialize execution state
    _initialize_execution_state()

    # Read configuration from session state
    provider_from_state, include_researcher, include_analyst, include_synthesiser = (
        _get_session_config(provider)
    )
    token_limit: int | None = st.session_state.get("token_limit")

    # Display current configuration
    agents_text = _format_enabled_agents(include_researcher, include_analyst, include_synthesiser)
    _display_configuration(provider_from_state, token_limit, agents_text)

    query = text_input(RUN_APP_QUERY_PLACEHOLDER)

    subheader(OUTPUT_SUBHEADER)

    # Handle button click - start new execution
    if button(RUN_APP_BUTTON):
        if query:
            # Start background execution
            info(f"{RUN_APP_QUERY_RUN_INFO} {query}")
            await _execute_query_background(
                query,
                provider_from_state,
                include_researcher,
                include_analyst,
                include_synthesiser,
                chat_config_file,
                token_limit,
            )
            # Force rerun to show updated state
            st.rerun()
        else:
            warning(RUN_APP_QUERY_WARNING)

    # Display execution status based on state
    execution_state = _get_execution_state()
    _display_execution_result(execution_state)

    # Render debug log panel
    _render_debug_log_panel()
