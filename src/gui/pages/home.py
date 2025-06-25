from streamlit import header, info, markdown

from gui.config.text import HOME_DESCRIPTION, HOME_HEADER, HOME_INFO


def render_home():
    header(HOME_HEADER)
    markdown(HOME_DESCRIPTION)
    info(HOME_INFO)
