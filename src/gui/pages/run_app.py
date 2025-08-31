"""
Streamlit interface for running the agentic system interactively.

This module defines the render_app function, which provides a Streamlit-based UI
for users to select a provider, enter a query, and execute the main agent workflow.
Results and errors are displayed in real time, supporting asynchronous execution.
"""

from pathlib import Path

from streamlit import button, exception, header, info, subheader, text_input, warning

from app.app import main
from app.utils.log import logger
from gui.components.output import render_output
from gui.config.text import (
    OUTPUT_SUBHEADER,
    RUN_APP_BUTTON,
    RUN_APP_HEADER,
    RUN_APP_OUTPUT_PLACEHOLDER,
    RUN_APP_PROVIDER_PLACEHOLDER,
    RUN_APP_QUERY_PLACEHOLDER,
    RUN_APP_QUERY_RUN_INFO,
    RUN_APP_QUERY_WARNING,
)


async def render_app(
    provider: str | None = None, chat_config_file: str | Path | None = None
):
    """
    Render the main app interface for running agentic queries via Streamlit.

    Displays input fields for provider and query, a button to trigger execution,
    and an area for output or error messages. Handles async invocation of the
    main agent workflow and logs any exceptions.
    """

    header(RUN_APP_HEADER)
    if provider is None:
        provider = text_input(RUN_APP_PROVIDER_PLACEHOLDER)
    query = text_input(RUN_APP_QUERY_PLACEHOLDER)

    subheader(OUTPUT_SUBHEADER)
    if button(RUN_APP_BUTTON):
        if query:
            info(f"{RUN_APP_QUERY_RUN_INFO} {query}")
            try:
                result = await main(
                    chat_provider=provider,
                    query=query,
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
