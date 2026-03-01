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

# Reason: Only themes with light backgrounds where dark text is needed for contrast
_LIGHT_THEMES: frozenset[str] = frozenset({"nord_light"})


def get_active_theme_name() -> str:
    """Get the name of the currently selected theme.

    Reads ``st.session_state["selected_theme"]``. Falls back to
    ``"expanse_dark"`` when the key is missing.

    Returns:
        str: Theme name string (e.g. ``"expanse_dark"``, ``"nord_light"``).
    """
    return st.session_state.get("selected_theme", _DEFAULT_THEME)


def get_active_theme() -> dict[str, str]:
    """Get the active theme dict from session state.

    Reads ``st.session_state["selected_theme"]`` and returns the matching
    entry from :data:`THEMES`. Falls back to *expanse_dark* when the key
    is missing or contains an unknown theme name.

    Returns:
        dict[str, str]: Theme color mapping with keys like ``primaryColor``,
            ``accentColor``, etc.
    """
    theme_name = get_active_theme_name()
    return THEMES.get(theme_name, THEMES[_DEFAULT_THEME])


def is_light_theme(theme_name: str) -> bool:
    """Check whether a theme name refers to a light theme.

    Args:
        theme_name: Name of the theme to check.

    Returns:
        bool: True if the theme is a light theme, False otherwise.
    """
    return theme_name in _LIGHT_THEMES


def get_graph_font_color() -> str:
    """Get the font color for Pyvis graph labels based on active theme.

    Returns ``"#000000"`` for light themes (>= 4.5:1 contrast on light bg)
    and ``"#ECEFF4"`` for dark themes (>= 4.5:1 contrast on dark bg).

    Returns:
        str: Hex color string for graph label text.
    """
    theme_name = get_active_theme_name()
    if is_light_theme(theme_name):
        return "#000000"
    return "#ECEFF4"


def get_theme_node_colors() -> tuple[str, str]:
    """Get node colors for agent graph from the active theme.

    Returns:
        tuple[str, str]: ``(primaryColor, accentColor)`` from the active theme.
            *primaryColor* is used for agent nodes, *accentColor* for tool nodes.
    """
    theme = get_active_theme()
    return theme["primaryColor"], theme["accentColor"]


def get_graph_node_colors() -> tuple[str, str]:
    """Get node colors for agent graph from the active theme.

    Alias for :func:`get_theme_node_colors` used by agent_graph.py.

    Returns:
        tuple[str, str]: ``(primaryColor, accentColor)`` from the active theme.
            *primaryColor* is used for agent nodes, *accentColor* for tool nodes.
    """
    return get_theme_node_colors()


def get_theme_bgcolor() -> str:
    """Get the background color from the active theme dict.

    Reads ``backgroundColor`` from the active theme in :data:`THEMES`.
    Falls back to Streamlit's ``theme.backgroundColor`` option, then
    to ``"#ffffff"`` as a last resort.

    Returns:
        str: Hex color string for the theme background.
    """
    theme = get_active_theme()
    bg = theme.get("backgroundColor")
    if isinstance(bg, str) and bg.startswith("#"):
        return bg
    # Reason: Fallback to Streamlit option when theme dict lacks backgroundColor
    st_bg = st.get_option("theme.backgroundColor")
    if isinstance(st_bg, str) and st_bg.startswith("#"):
        return st_bg
    return "#ffffff"
