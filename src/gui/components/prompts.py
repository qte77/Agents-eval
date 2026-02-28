from streamlit import text_area


def render_prompt_editor(prompt_name: str, prompt_value: str, height: int = 150) -> str | None:
    """Render a read-only prompt text area for display.

    Args:
        prompt_name: Snake_case prompt key used to generate the label.
        prompt_value: Current prompt text content.
        height: Text area height in pixels.

    Returns:
        The displayed prompt value (always unchanged since field is read-only).
    """
    return text_area(
        f"{prompt_name.replace('_', ' ').title()}",
        value=prompt_value,
        height=height,
        disabled=True,
        help="Read-only. Edit config_chat.json to modify prompts.",
    )
