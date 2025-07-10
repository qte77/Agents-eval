"""
Streamlit component for editing agent system prompts.

This module provides a function to render and edit prompt configurations
for agent roles using a Streamlit-based UI. It validates the input configuration,
displays warnings if prompts are missing, and allows interactive editing of each prompt.
"""

from pydantic import BaseModel
from streamlit import error, header, warning

from app.datamodels.app_models import ChatConfig
from app.utils.error_messages import invalid_type
from app.utils.log import logger
from gui.components.prompts import render_prompt_editor
from gui.config.config import PROMPTS_DEFAULT
from gui.config.text import PROMPTS_HEADER, PROMPTS_WARNING


def render_prompts(chat_config: ChatConfig | BaseModel):  # -> dict[str, str]:
    """
    Render and edit the prompt configuration for agent roles in the Streamlit UI.
    """

    header(PROMPTS_HEADER)

    if not isinstance(chat_config, ChatConfig):
        msg = invalid_type("ChatConfig", type(chat_config).__name__)
        logger.error(msg)
        error(msg)
        return None

    # updated = False
    prompts = chat_config.prompts

    if not prompts:
        warning(PROMPTS_WARNING)
        prompts = PROMPTS_DEFAULT

    updated_prompts = prompts.copy()

    # Edit prompts
    for prompt_key, prompt_value in prompts.items():
        new_value = render_prompt_editor(prompt_key, prompt_value, height=200)
        if new_value != prompt_value and new_value is not None:
            updated_prompts[prompt_key] = new_value
            # updated = True

    # return updated_prompts if updated else prompts
