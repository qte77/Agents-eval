from streamlit import sidebar

from gui.config.config import PAGES, PHOENIX_DEFAULT_ENDPOINT


def render_sidebar(sidebar_title: str, execution_state: str = "idle") -> str:
    """Render sidebar with page navigation, Phoenix trace link, and execution indicator.

    Args:
        sidebar_title: Title to display in the sidebar.
        execution_state: Current execution state — 'idle', 'running', 'completed', or 'error'.
            When 'running', an in-progress indicator is shown at the top of the sidebar.

    Returns:
        Selected page name from the radio button selection.
    """
    sidebar.title(sidebar_title)

    # S8-F3.3: execution-in-progress indicator (WCAG 4.1.3)
    if execution_state == "running":
        sidebar.info("⏳ Execution in progress…")

    # S8-F8.1: WCAG 1.3.1, 2.4.6 — meaningful label with visual collapse avoids empty label
    selected_page = sidebar.radio("Navigation", PAGES, label_visibility="collapsed")

    # Phoenix trace viewer link
    sidebar.divider()
    sidebar.markdown("### 🔍 Trace Viewer")
    # S8-F8.1: "(opens in new tab)" warns users of external navigation
    sidebar.markdown(
        f"[Open Phoenix Traces (opens in new tab)]({PHOENIX_DEFAULT_ENDPOINT})",
        help="View detailed execution traces in Arize Phoenix",
    )
    sidebar.caption("Phoenix must be running locally on port 6006")

    return selected_page
