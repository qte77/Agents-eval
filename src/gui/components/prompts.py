from streamlit import text_area


def render_prompt_editor(
    prompt_name: str, prompt_value: str, height: int = 150
) -> str | None:
    return text_area(
        f"{prompt_name.replace('_', ' ').title()}", value=prompt_value, height=height
    )
