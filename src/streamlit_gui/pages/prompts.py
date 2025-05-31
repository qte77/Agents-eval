import src.streamlit as st
from streamlit_gui.components.prompts import render_prompt_editor

TA_HEIGHT = 50


def render_prompts(prompts):
    st.header("Agent Prompts")

    updated = False
    updated_prompts = prompts.copy()

    if not prompts:
        prompts = {
            "system_prompt_manager": (
                "You are a manager overseeing research and analysis tasks..."
            ),
            "system_prompt_researcher": (
                "You are a researcher. Gather and analyze data..."
            ),
            "system_prompt_analyst": (
                "You are a research analyst. Use your analytical skills..."
            ),
            "system_prompt_synthesiser": (
                "You are a research synthesiser. Use your analytical skills..."
            ),
        }

    # Edit prompts
    for prompt_key, prompt_value in prompts.items():
        new_value = render_prompt_editor(prompt_key, prompt_value, height=200)
        if new_value != prompt_value:
            updated_prompts[prompt_key] = new_value
            updated = True

    return updated_prompts if updated else prompts
