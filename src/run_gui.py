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
from sys import path

# rebase project root path to avoid import errors
project_root = Path(__file__).parent.parent
path.insert(0, str(project_root))

from src.app.config.config_app import (  # noqa: E402
    CHAT_CONFIG_FILE,
    CHAT_DEFAULT_PROVIDER,
)
from src.app.datamodels.app_models import ChatConfig  # noqa: E402
from src.app.utils.load_configs import load_config  # noqa: E402
from src.app.utils.log import logger  # noqa: E402
from src.gui.components.sidebar import render_sidebar  # noqa: E402
from src.gui.config.config import APP_PATH  # noqa: E402
from src.gui.config.styling import add_custom_styling  # noqa: E402
from src.gui.config.text import PAGE_TITLE  # noqa: E402
from src.gui.pages.home import render_home  # noqa: E402
from src.gui.pages.prompts import render_prompts  # noqa: E402
from src.gui.pages.run_app import render_app  # noqa: E402
from src.gui.pages.settings import render_settings  # noqa: E402

# TODO create sidebar tabs, move settings to page,
# set readme.md as home, separate prompts into page

chat_config_pfile = Path(__file__).parent / APP_PATH / CHAT_CONFIG_FILE
chat_config = load_config(chat_config_pfile, ChatConfig)
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
        render_prompts(chat_config)
    elif selected_page == "App":
        logger.info(f"Page 'App' provider: {CHAT_DEFAULT_PROVIDER}")
        await render_app(CHAT_DEFAULT_PROVIDER)


if __name__ == "__main__":
    run(main())
