from streamlit import set_page_config


def add_custom_styling(page_title: str):
    set_page_config(
        page_title=f"{page_title}",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # S8-F8.1: WCAG 1.3.3, 1.4.1 — native selection indicators must not be hidden via CSS
