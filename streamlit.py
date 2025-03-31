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
from os import path

from src.utils.utils import load_config
from streamlit_gui.components.sidebar import render_sidebar
from streamlit_gui.pages.home import render_home
from streamlit_gui.pages.prompts import render_prompts
from streamlit_gui.pages.run_app import render_app
from streamlit_gui.pages.settings import render_settings
from streamlit_gui.utils.styling import add_custom_styling

# TODO create sidebar tabs, move settings to page,
# set readme.md as home, separate prompts into page


PAGE_TITLE = "MAS Eval 👾⚗️🧠💡"
CONFIG_PATH = path.join(path.dirname(__file__), "src/config.json")
CONFIG = load_config(CONFIG_PATH)
provider = "huggingface"

print(f"Selected provider: {provider}")


async def main():
    add_custom_styling(PAGE_TITLE)
    selected_page = render_sidebar(PAGE_TITLE)

    if selected_page == "Home":
        render_home()
    elif selected_page == "Settings":
        provider = render_settings(CONFIG)
        print(f"provider: {provider}")
    elif selected_page == "Prompts":
        render_prompts(CONFIG.prompts)  # prompts =
    elif selected_page == "App":
        print(f"provider: {provider}")
        await render_app(provider)


if __name__ == "__main__":
    run(main())
