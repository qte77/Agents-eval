from streamlit import set_page_config

THEMES: dict[str, dict[str, str]] = {
    "expanse_dark": {
        "primaryColor": "#4A90E2",
        "backgroundColor": "#0b0c10",
        "secondaryBackgroundColor": "#1f2833",
        "textColor": "#66fcf1",
        "accentColor": "#50C878",
    },
    "nord_light": {
        "primaryColor": "#5E81AC",
        "backgroundColor": "#ECEFF4",
        "secondaryBackgroundColor": "#E5E9F0",
        "textColor": "#2E3440",
        "accentColor": "#88C0D0",
    },
    "tokyo_night": {
        "primaryColor": "#7AA2F7",
        "backgroundColor": "#1A1B26",
        "secondaryBackgroundColor": "#24283B",
        "textColor": "#C0CAF5",
        "accentColor": "#9ECE6A",
    },
}


def add_custom_styling(page_title: str):
    set_page_config(
        page_title=f"{page_title}",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # S8-F8.1: WCAG 1.3.3, 1.4.1 — native selection indicators must not be hidden via CSS
