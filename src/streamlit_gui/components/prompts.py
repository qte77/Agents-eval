import src.streamlit as st


def render_prompt_editor(prompt_name, prompt_value, height=150):
    return st.text_area(
        f"{prompt_name.replace('_', ' ').title()}", value=prompt_value, height=height
    )
