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

from streamlit_gui.app_config import load_app_config  # , save_config
from streamlit_gui.components.sidebar import render_sidebar
from streamlit_gui.pages.home import render_home
from streamlit_gui.pages.prompts import render_prompts
from streamlit_gui.pages.run_app import render_app
from streamlit_gui.pages.settings import render_settings
from streamlit_gui.styling import add_custom_styling

# TODO create sidebar tabs, move settings to page,
# set readme.md as home, separate prompts into page


page_title = "MAS Eval 👾⚗️🧠💡"


async def main():
    add_custom_styling(page_title)
    config = load_app_config()

    selected_page = render_sidebar(page_title)
    if selected_page == "Home":
        render_home()
    elif selected_page == "Settings":
        render_settings(config)
        # if updated_config:
        #    save_config(updated_config)
    elif selected_page == "Prompts":
        render_prompts(config.get("prompts", {}))
        # if updated_prompts:
        #    config["prompts"] = updated_prompts
        #    save_config(config)
    elif selected_page == "App":
        await render_app(config)


if __name__ == "__main__":
    run(main())
