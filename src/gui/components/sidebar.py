from streamlit import sidebar

from gui.config.config import PAGES, PHOENIX_DEFAULT_ENDPOINT


def render_sidebar(sidebar_title: str):
    """Render sidebar with page navigation and Phoenix trace viewer link.

    Args:
        sidebar_title: Title to display in the sidebar.

    Returns:
        Selected page name from the radio button selection.
    """
    sidebar.title(sidebar_title)
    selected_page = sidebar.radio(" ", PAGES)

    # Phoenix trace viewer link
    sidebar.divider()
    sidebar.markdown("### 🔍 Trace Viewer")
    sidebar.markdown(
        f"[Open Phoenix Traces]({PHOENIX_DEFAULT_ENDPOINT})",
        help="View detailed execution traces in Arize Phoenix",
    )
    sidebar.caption("Phoenix must be running locally on port 6006")

    return selected_page
