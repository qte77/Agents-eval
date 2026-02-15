"""
Streamlit interface for running the agentic system interactively.

This module defines the render_app function, which provides a Streamlit-based UI
for users to select a provider, enter a query, and execute the main agent workflow.
Results and errors are displayed in real time, supporting asynchronous execution.

Provider and sub-agent configuration are read from session state, allowing users
to configure these settings on the Settings page before running queries.
"""

from pathlib import Path

import streamlit as st
from streamlit import button, exception, header, info, subheader, text, text_input, warning

from app.app import main
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


async def render_app(provider: str | None = None, chat_config_file: str | Path | None = None):
    """
    Render the main app interface for running agentic queries via Streamlit.

    Displays input fields for provider and query, a button to trigger execution,
    and an area for output or error messages. Handles async invocation of the
    main agent workflow and logs any exceptions.

    Provider and sub-agent configuration are read from session state (configured
    on the Settings page).
    """

    header(RUN_APP_HEADER)

    # Read configuration from session state (with fallback to default provider)
    from app.config.config_app import CHAT_DEFAULT_PROVIDER

    provider_from_state: str = st.session_state.get("chat_provider", provider or CHAT_DEFAULT_PROVIDER)
    include_researcher: bool = st.session_state.get("include_researcher", False)
    include_analyst: bool = st.session_state.get("include_analyst", False)
    include_synthesiser: bool = st.session_state.get("include_synthesiser", False)

    # Display current configuration
    text(f"**Provider:** {provider_from_state}")
    enabled_agents: list[str] = []
    if include_researcher:
        enabled_agents.append("Researcher")
    if include_analyst:
        enabled_agents.append("Analyst")
    if include_synthesiser:
        enabled_agents.append("Synthesiser")
    agents_text: str = ", ".join(enabled_agents) if enabled_agents else "None (Manager only)"
    text(f"**Enabled Sub-Agents:** {agents_text}")

    query = text_input(RUN_APP_QUERY_PLACEHOLDER)

    subheader(OUTPUT_SUBHEADER)
    if button(RUN_APP_BUTTON):
        if query:
            info(f"{RUN_APP_QUERY_RUN_INFO} {query}")
            try:
                result = await main(
                    chat_provider=provider_from_state,
                    query=query,
                    include_researcher=include_researcher,
                    include_analyst=include_analyst,
                    include_synthesiser=include_synthesiser,
                    chat_config_file=chat_config_file,
                )
                render_output(result)
            except Exception as e:
                render_output(None)
                exception(e)
                logger.exception(e)
        else:
            warning(RUN_APP_QUERY_WARNING)
    else:
        render_output(RUN_APP_OUTPUT_PLACEHOLDER)
