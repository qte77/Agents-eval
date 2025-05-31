from streamlit import caption, divider


def render_footer(footer_caption: str):
    """Render the page footer."""
    divider()
    caption(footer_caption)
