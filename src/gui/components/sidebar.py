from streamlit import sidebar

from gui.config.config import PAGES


def render_sidebar(sidebar_title: str):
    sidebar.title(sidebar_title)
    selected_page = sidebar.radio(" ", PAGES)

    # st.sidebar.divider()
    # st.sidebar.info(" ")
    return selected_page
