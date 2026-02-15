"""
Streamlit settings UI for displaying application settings.

This module provides a function to display actual settings from pydantic-settings
classes (CommonSettings and JudgeSettings). Read-only display following YAGNI
principle - no save functionality as settings come from environment variables.

Also provides UI controls for chat provider selection and sub-agent configuration
with session state persistence.
"""

import streamlit as st
from streamlit import checkbox, expander, header, selectbox, text

from app.common.settings import CommonSettings
from app.data_models.app_models import PROVIDER_REGISTRY
from app.judge.settings import JudgeSettings
from app.utils.log import logger
from gui.config.text import SETTINGS_HEADER


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
    with expander("Agent Configuration", expanded=True):
        # Provider selection with all providers from PROVIDER_REGISTRY
        provider_options = list(PROVIDER_REGISTRY.keys())
        current_provider_idx = (
            provider_options.index(st.session_state["chat_provider"])
            if st.session_state["chat_provider"] in provider_options
            else 0
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

    # Common Settings Section
    with expander("Common Settings", expanded=True):
        text(f"Log Level: {common_settings.log_level}")
        text(f"Enable Logfire: {common_settings.enable_logfire}")
        text(f"Max Content Length: {common_settings.max_content_length}")

    # Judge Settings - Tier Configuration
    with expander("Judge Settings - Tier Configuration"):
        text(f"Enabled Tiers: {judge_settings.tiers_enabled}")
        text(f"Tier 1 Max Seconds: {judge_settings.tier1_max_seconds}")
        text(f"Tier 2 Max Seconds: {judge_settings.tier2_max_seconds}")
        text(f"Tier 3 Max Seconds: {judge_settings.tier3_max_seconds}")
        text(f"Total Max Seconds: {judge_settings.total_max_seconds}")

    # Judge Settings - Composite Scoring
    with expander("Judge Settings - Composite Scoring"):
        text(f"Accept Threshold: {judge_settings.composite_accept_threshold}")
        text(f"Weak Accept Threshold: {judge_settings.composite_weak_accept_threshold}")
        text(f"Weak Reject Threshold: {judge_settings.composite_weak_reject_threshold}")
        text(f"Fallback Strategy: {judge_settings.fallback_strategy}")

    # Judge Settings - Tier 2 LLM Judge
    with expander("Judge Settings - Tier 2 LLM Judge"):
        text(f"Provider: {judge_settings.tier2_provider}")
        text(f"Model: {judge_settings.tier2_model}")
        text(f"Fallback Provider: {judge_settings.tier2_fallback_provider}")
        text(f"Fallback Model: {judge_settings.tier2_fallback_model}")
        text(f"Max Retries: {judge_settings.tier2_max_retries}")
        text(f"Timeout Seconds: {judge_settings.tier2_timeout_seconds}")

    # Judge Settings - Observability
    with expander("Judge Settings - Observability"):
        text(f"Trace Collection: {judge_settings.trace_collection}")
        text(f"Trace Storage Path: {judge_settings.trace_storage_path}")
        text(f"Logfire Enabled: {judge_settings.logfire_enabled}")
        text(f"Logfire Send to Cloud: {judge_settings.logfire_send_to_cloud}")
        text(f"Phoenix Endpoint: {judge_settings.phoenix_endpoint}")
        text(f"Performance Logging: {judge_settings.performance_logging}")
