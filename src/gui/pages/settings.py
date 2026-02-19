"""
Streamlit settings UI for displaying and editing application settings.

This module provides a function to display and edit settings from pydantic-settings
classes (CommonSettings and JudgeSettings). Settings are editable via the GUI and
applied to the current session via st.session_state.

Also provides UI controls for chat provider selection and sub-agent configuration
with session state persistence.
"""

import streamlit as st
from streamlit import button, checkbox, expander, header, number_input, selectbox, text, text_input

from app.common.settings import CommonSettings
from app.data_models.app_models import PROVIDER_REGISTRY
from app.judge.settings import JudgeSettings
from app.utils.load_configs import load_config
from app.utils.log import logger
from app.utils.paths import resolve_config_path
from gui.config.text import SETTINGS_HEADER


def _render_agent_configuration() -> None:
    """Render agent configuration section with provider and sub-agent toggles."""
    # Reason: Only render when session_state is available (not in tests)
    if not hasattr(st, "session_state"):
        return

    with expander("Agent Configuration", expanded=True):
        # Provider selection with all providers from PROVIDER_REGISTRY
        provider_options = list(PROVIDER_REGISTRY.keys())
        current_provider = st.session_state.get("chat_provider")
        current_provider_idx = (
            provider_options.index(current_provider) if current_provider in provider_options else 0
        )
        st.session_state["chat_provider"] = selectbox(
            "Chat Provider",
            options=provider_options,
            index=current_provider_idx,
            key="provider_selectbox",
        )

        # Sub-agent toggles
        text("**Enable Sub-Agents:**")
        st.session_state["include_researcher"] = checkbox(
            "Include Researcher Agent",
            value=st.session_state.get("include_researcher", False),
            key="researcher_checkbox",
        )
        st.session_state["include_analyst"] = checkbox(
            "Include Analyst Agent",
            value=st.session_state.get("include_analyst", False),
            key="analyst_checkbox",
        )
        st.session_state["include_synthesiser"] = checkbox(
            "Include Synthesiser Agent",
            value=st.session_state.get("include_synthesiser", False),
            key="synthesiser_checkbox",
        )

        # Token limit configuration
        from app.config.config_app import CHAT_CONFIG_FILE  # type: ignore[reportUnusedImport]
        from app.data_models.app_models import ChatConfig  # type: ignore[reportUnusedImport]

        config_path = resolve_config_path(CHAT_CONFIG_FILE)
        chat_config = load_config(config_path, ChatConfig)
        current_provider_val = st.session_state.get("chat_provider", "ollama")
        provider_config = chat_config.providers.get(current_provider_val)  # type: ignore[reportAttributeAccessIssue]
        default_limit = (
            provider_config.usage_limits
            if provider_config and provider_config.usage_limits
            else 25000
        )

        text("**Token Limit:**")
        st.session_state["token_limit"] = number_input(
            "Agent Token Limit",
            min_value=1000,
            max_value=1000000,
            value=st.session_state.get("token_limit", default_limit),
            step=1000,
            help="Override token limit (1000-1000000). Default from config_chat.json.",
            key="token_limit_input",
        )


def _render_tier_configuration(judge_settings: JudgeSettings) -> None:
    """Render tier configuration section with editable timeout values."""
    with expander("Judge Settings - Tier Configuration", expanded=True):
        st.session_state["judge_tier1_max_seconds"] = number_input(
            "Tier 1 Max Seconds",
            min_value=0.1,
            max_value=300.0,
            value=st.session_state.get("judge_tier1_max_seconds", judge_settings.tier1_max_seconds),
            step=0.1,
            key="tier1_max_seconds_input",
            help="Tier 1 timeout (Traditional Metrics). Range: 0.1-300 seconds.",
        )
        st.session_state["judge_tier2_max_seconds"] = number_input(
            "Tier 2 Max Seconds",
            min_value=0.1,
            max_value=300.0,
            value=st.session_state.get("judge_tier2_max_seconds", judge_settings.tier2_max_seconds),
            step=0.1,
            key="tier2_max_seconds_input",
            help="Tier 2 timeout (LLM-as-Judge). Range: 0.1-300 seconds.",
        )
        st.session_state["judge_tier3_max_seconds"] = number_input(
            "Tier 3 Max Seconds",
            min_value=0.1,
            max_value=300.0,
            value=st.session_state.get("judge_tier3_max_seconds", judge_settings.tier3_max_seconds),
            step=0.1,
            key="tier3_max_seconds_input",
            help="Tier 3 timeout (Graph Analysis). Range: 0.1-300 seconds.",
        )
        st.session_state["judge_total_max_seconds"] = number_input(
            "Total Max Seconds",
            min_value=0.1,
            max_value=300.0,
            value=st.session_state.get("judge_total_max_seconds", judge_settings.total_max_seconds),
            step=0.1,
            key="total_max_seconds_input",
            help="Total pipeline timeout. Range: 0.1-300 seconds.",
        )


def _render_composite_scoring(judge_settings: JudgeSettings) -> None:
    """Render composite scoring section with editable threshold values."""
    with expander("Judge Settings - Composite Scoring"):
        st.session_state["judge_composite_accept_threshold"] = number_input(
            "Accept Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get(
                "judge_composite_accept_threshold", judge_settings.composite_accept_threshold
            ),
            step=0.01,
            key="composite_accept_threshold_input",
            help="Score threshold for 'accept' recommendation. Range: 0.0-1.0.",
        )
        st.session_state["judge_composite_weak_accept_threshold"] = number_input(
            "Weak Accept Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get(
                "judge_composite_weak_accept_threshold",
                judge_settings.composite_weak_accept_threshold,
            ),
            step=0.01,
            key="composite_weak_accept_threshold_input",
            help="Score threshold for 'weak_accept'. Range: 0.0-1.0.",
        )
        st.session_state["judge_composite_weak_reject_threshold"] = number_input(
            "Weak Reject Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get(
                "judge_composite_weak_reject_threshold",
                judge_settings.composite_weak_reject_threshold,
            ),
            step=0.01,
            key="composite_weak_reject_threshold_input",
            help="Score threshold for 'weak_reject'. Range: 0.0-1.0.",
        )


def _render_tier2_llm_judge(judge_settings: JudgeSettings) -> None:
    """Render Tier 2 LLM judge section with editable provider/model fields."""
    with expander("Judge Settings - Tier 2 LLM Judge"):
        st.session_state["judge_tier2_provider"] = text_input(
            "Provider",
            value=st.session_state.get("judge_tier2_provider", judge_settings.tier2_provider),
            key="tier2_provider_input",
            help="LLM provider for Tier 2 evaluation (e.g., 'openai', 'github', 'auto').",
        )
        st.session_state["judge_tier2_model"] = text_input(
            "Model",
            value=st.session_state.get("judge_tier2_model", judge_settings.tier2_model),
            key="tier2_model_input",
            help="LLM model for Tier 2 evaluation (e.g., 'gpt-4o-mini').",
        )
        st.session_state["judge_tier2_fallback_provider"] = text_input(
            "Fallback Provider",
            value=st.session_state.get(
                "judge_tier2_fallback_provider", judge_settings.tier2_fallback_provider
            ),
            key="tier2_fallback_provider_input",
            help="Fallback LLM provider if primary fails.",
        )
        st.session_state["judge_tier2_fallback_model"] = text_input(
            "Fallback Model",
            value=st.session_state.get(
                "judge_tier2_fallback_model", judge_settings.tier2_fallback_model
            ),
            key="tier2_fallback_model_input",
            help="Fallback LLM model if primary fails.",
        )
        st.session_state["judge_tier2_timeout_seconds"] = number_input(
            "Timeout Seconds",
            min_value=0.1,
            max_value=300.0,
            value=st.session_state.get(
                "judge_tier2_timeout_seconds", judge_settings.tier2_timeout_seconds
            ),
            step=0.1,
            key="tier2_timeout_seconds_input",
            help="Request timeout for LLM calls. Range: 0.1-300 seconds.",
        )


def _render_observability_settings(judge_settings: JudgeSettings) -> None:
    """Render observability settings section with editable boolean and URL fields."""
    with expander("Judge Settings - Observability"):
        st.session_state["judge_logfire_enabled"] = checkbox(
            "Logfire Enabled",
            value=st.session_state.get("judge_logfire_enabled", judge_settings.logfire_enabled),
            key="logfire_enabled_checkbox",
            help="Enable Logfire tracing.",
        )
        st.session_state["judge_phoenix_endpoint"] = text_input(
            "Phoenix Endpoint",
            value=st.session_state.get("judge_phoenix_endpoint", judge_settings.phoenix_endpoint),
            key="phoenix_endpoint_input",
            help="Phoenix local trace viewer endpoint (e.g., 'http://localhost:6006').",
        )
        st.session_state["judge_trace_collection"] = checkbox(
            "Trace Collection",
            value=st.session_state.get("judge_trace_collection", judge_settings.trace_collection),
            key="trace_collection_checkbox",
            help="Enable trace collection.",
        )


def _render_common_settings(common_settings: CommonSettings) -> None:
    """Render editable Common Settings section with tooltips.

    Displays log level selectbox and max content length number input,
    storing selections to session state with the 'common_' prefix.
    Logfire is consolidated to JudgeSettings (not shown here).

    Args:
        common_settings: CommonSettings instance with default values.
    """
    with expander("Common Settings", expanded=True):
        st.session_state["common_log_level"] = selectbox(
            "Log Level",
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            index=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].index(
                st.session_state.get("common_log_level", common_settings.log_level)
            ),
            key="common_log_level_selectbox",
            help=(
                "Controls application logging verbosity. "
                "DEBUG shows all messages; CRITICAL shows only fatal errors."
            ),
        )
        st.session_state["common_max_content_length"] = number_input(
            "Max Content Length",
            min_value=1000,
            max_value=100000,
            value=st.session_state.get(
                "common_max_content_length", common_settings.max_content_length
            ),
            step=1000,
            key="common_max_content_length_input",
            help=(
                "Maximum number of characters for paper content passed to agents. "
                "Valid range: 1000–100000."
            ),
        )


def _render_reset_button() -> None:
    """Render reset to defaults button and handle reset logic."""
    if button("Reset to Defaults"):
        # Clear all judge and common settings from session state
        keys_to_clear = [
            k
            for k in st.session_state.keys()
            if isinstance(k, str) and (k.startswith("judge_") or k.startswith("common_"))
        ]
        for key in keys_to_clear:
            del st.session_state[key]
        st.rerun()


def render_settings(common_settings: CommonSettings, judge_settings: JudgeSettings) -> None:
    """
    Render application settings in the Streamlit UI.

    Displays actual default values from CommonSettings and JudgeSettings
    pydantic-settings classes. Read-only display using Streamlit expanders
    to organize settings by category.

    Also provides UI controls for chat provider selection and sub-agent configuration
    with session state persistence across page navigation.

    Args:
        common_settings: CommonSettings instance with application-level configuration
        judge_settings: JudgeSettings instance with evaluation pipeline configuration
    """
    header(SETTINGS_HEADER)

    logger.info("Displaying actual settings from pydantic-settings classes")

    # Agent Configuration Section
    _render_agent_configuration()

    # Common Settings Section (editable)
    _render_common_settings(common_settings)

    # Judge Settings - Editable Sections
    _render_tier_configuration(judge_settings)
    _render_composite_scoring(judge_settings)
    _render_tier2_llm_judge(judge_settings)
    _render_observability_settings(judge_settings)

    # Reset to Defaults Button
    _render_reset_button()
