"""
This module sets up and runs a Streamlit application for a Multi-Agent System.

The application includes the following components:
- Header
- Sidebar for configuration options
- Main content area for prompts
- Footer

The main function loads the configuration, renders the UI components, and handles the
execution of the Multi-Agent System based on user input.

Functions:
- run_app(): Placeholder function to run the main application logic.
- main(): Main function to set up and run the Streamlit application.
"""

from asyncio import run
from pathlib import Path

import streamlit as st

from app.common.settings import CommonSettings
from app.config.config_app import (
    CHAT_CONFIG_FILE,
    CHAT_DEFAULT_PROVIDER,
)
from app.data_models.app_models import ChatConfig
from app.judge.settings import JudgeSettings
from app.utils.load_configs import load_config
from app.utils.log import logger
from gui.components.sidebar import render_sidebar
from gui.config.config import APP_CONFIG_PATH
from gui.config.styling import add_custom_styling
from gui.config.text import PAGE_TITLE
from gui.pages.agent_graph import render_agent_graph
from gui.pages.evaluation import render_evaluation
from gui.pages.home import render_home
from gui.pages.prompts import render_prompts
from gui.pages.run_app import render_app
from gui.pages.settings import render_settings

# TODO create sidebar tabs, move settings to page,
# set readme.md as home, separate prompts into page

chat_config_file = Path(__file__).parent / APP_CONFIG_PATH / CHAT_CONFIG_FILE
chat_config = load_config(chat_config_file, ChatConfig)
common_settings = CommonSettings()
judge_settings = JudgeSettings()
provider = CHAT_DEFAULT_PROVIDER
logger.info(f"Default provider in GUI: {CHAT_DEFAULT_PROVIDER}")


def get_session_state_defaults() -> dict[str, str | bool]:
    """
    Get default values for session state.

    Returns:
        Dict with default provider and sub-agent configuration flags
    """
    return {
        "chat_provider": CHAT_DEFAULT_PROVIDER,
        "include_researcher": False,
        "include_analyst": False,
        "include_synthesiser": False,
    }


def initialize_session_state() -> None:
    """
    Initialize session state with default values if not already set.

    Uses st.session_state to persist user selections across page navigation.
    """
    defaults = get_session_state_defaults()
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


async def main():
    # Initialize session state before rendering any pages
    initialize_session_state()

    add_custom_styling(PAGE_TITLE)
    selected_page = render_sidebar(PAGE_TITLE)

    if selected_page == "Home":
        render_home()
    elif selected_page == "Settings":
        # Display actual settings from pydantic-settings classes
        render_settings(common_settings, judge_settings)
    elif selected_page == "Prompts":
        render_prompts(chat_config)
    elif selected_page == "App":
        logger.info(f"Page 'App' provider: {CHAT_DEFAULT_PROVIDER}")
        await render_app(CHAT_DEFAULT_PROVIDER, chat_config_file)
    elif selected_page == "Evaluation Results":
        # Render with None initially - real data would come from session state
        render_evaluation(None)
    elif selected_page == "Agent Graph":
        # Render with None initially - real data would come from session state
        render_agent_graph(None)


if __name__ == "__main__":
    run(main())
