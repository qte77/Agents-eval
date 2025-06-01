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

from app.config_app import CHAT_CONFIG_FILE, CHAT_DEFAULT_PROVIDER
from app.utils.load_settings import load_config
from app.utils.log import logger
from gui.components.sidebar import render_sidebar
from gui.pages.home import render_home
from gui.pages.prompts import render_prompts
from gui.pages.run_app import render_app
from gui.pages.settings import render_settings
from gui.utils.config import APP_PATH
from gui.utils.styling import add_custom_styling
from gui.utils.text import PAGE_TITLE

# TODO create sidebar tabs, move settings to page,
# set readme.md as home, separate prompts into page

chat_config_pfile = Path(__file__).parent / APP_PATH / CHAT_CONFIG_FILE
chat_config = load_config(chat_config_pfile)
provider = CHAT_DEFAULT_PROVIDER
logger.info(f"Default provider: {CHAT_DEFAULT_PROVIDER}")


async def main():
    add_custom_styling(PAGE_TITLE)
    selected_page = render_sidebar(PAGE_TITLE)

    if selected_page == "Home":
        render_home()
    elif selected_page == "Settings":
        # TODO temp save settings to be used in gui
        provider = render_settings(chat_config)
        logger.info(f"Page 'Settings' provider: {provider}")
    elif selected_page == "Prompts":
        render_prompts(chat_config.prompts)  # prompts =
    elif selected_page == "App":
        logger.info(f"Page 'App' provider: {CHAT_DEFAULT_PROVIDER}")
        await render_app(CHAT_DEFAULT_PROVIDER)


if __name__ == "__main__":
    run(main())
