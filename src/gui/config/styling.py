import streamlit as st
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


_DEFAULT_THEME = "expanse_dark"


def get_active_theme() -> dict[str, str]:
    """Get the active theme dict from session state.

    Reads ``st.session_state["selected_theme"]`` and returns the matching
    entry from :data:`THEMES`. Falls back to *expanse_dark* when the key
    is missing or contains an unknown theme name.

    Returns:
        dict[str, str]: Theme color mapping with keys like ``primaryColor``,
            ``accentColor``, etc.
    """
    theme_name = st.session_state.get("selected_theme", _DEFAULT_THEME)
    return THEMES.get(theme_name, THEMES[_DEFAULT_THEME])


def get_theme_node_colors() -> tuple[str, str]:
    """Get node colors for agent graph from the active theme.

    Returns:
        tuple[str, str]: ``(primaryColor, accentColor)`` from the active theme.
            *primaryColor* is used for agent nodes, *accentColor* for tool nodes.
    """
    theme = get_active_theme()
    return theme["primaryColor"], theme["accentColor"]


def get_theme_bgcolor() -> str:
    """Get the background color from the current Streamlit theme.

    Returns:
        str: Hex color string for the theme background (e.g. '#ffffff' or '#0e1117').
    """
    theme = st.get_option("theme.backgroundColor")
    if isinstance(theme, str) and theme.startswith("#"):
        return theme
    # Reason: Streamlit default light theme background when theme is not configured
    return "#ffffff"
