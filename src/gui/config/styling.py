"""GUI theming utilities.

Provides helper functions that read the **active Streamlit theme** (light or
dark) and return colors for custom elements such as the Pyvis agent graph.

Theme colors are defined in ``.streamlit/config.toml`` via the native
``[theme.dark]`` and ``[theme.light]`` sections.  Users switch themes through
Streamlit's built-in Settings menu (hamburger icon → Settings → Theme).

The ``THEMES`` dict below mirrors those config values so that non-Streamlit
components (Pyvis, custom HTML) can access the palette at runtime.
"""

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

_DARK_THEME = "expanse_dark"
_LIGHT_THEME = "nord_light"


def add_custom_styling(page_title: str):
    """Configure the Streamlit page layout.

    Args:
        page_title: Title shown in the browser tab.
    """
    set_page_config(
        page_title=f"{page_title}",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # S8-F8.1: WCAG 1.3.3, 1.4.1 — native selection indicators must not be hidden via CSS


def _is_streamlit_light_mode() -> bool:
    """Detect whether Streamlit is currently rendering in light mode.

    Uses ``st.get_option("theme.backgroundColor")`` to infer the active mode.
    A background color with high luminance (>= 0x80 average) is considered light.

    Returns:
        bool: True when the active Streamlit theme is light.
    """
    bg = st.get_option("theme.backgroundColor")
    if isinstance(bg, str) and bg.startswith("#") and len(bg) == 7:
        r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
        return (r + g + b) / 3 >= 0x80
    return False


def get_active_theme_name() -> str:
    """Get the name of the currently active theme.

    Detects Streamlit's active theme (light or dark) and returns the
    corresponding theme name from :data:`THEMES`.

    Returns:
        str: Theme name string (``"nord_light"`` or ``"expanse_dark"``).
    """
    return _LIGHT_THEME if _is_streamlit_light_mode() else _DARK_THEME


def get_active_theme() -> dict[str, str]:
    """Get the active theme dict based on Streamlit's current mode.

    Returns:
        dict[str, str]: Theme color mapping with keys like ``primaryColor``,
            ``accentColor``, etc.
    """
    return THEMES[get_active_theme_name()]


def is_light_theme(theme_name: str) -> bool:
    """Check whether a theme name refers to a light theme.

    Args:
        theme_name: Name of the theme to check.

    Returns:
        bool: True if the theme is a light theme, False otherwise.
    """
    return theme_name == _LIGHT_THEME


def get_graph_font_color() -> str:
    """Get the font color for Pyvis graph labels based on active theme.

    Returns ``"#000000"`` for light themes (>= 4.5:1 contrast on light bg)
    and ``"#ECEFF4"`` for dark themes (>= 4.5:1 contrast on dark bg).

    Returns:
        str: Hex color string for graph label text.
    """
    if _is_streamlit_light_mode():
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
