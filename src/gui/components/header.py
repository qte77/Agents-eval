from streamlit import divider, title


def render_header(header_title: str):
    """Render the page header with title."""
    title(header_title)
    divider()
