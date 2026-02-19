"""
Streamlit component for displaying agent system prompts.

This module provides a function to display prompt configurations
for agent roles using a Streamlit-based UI. Loads prompts directly
from ChatConfig without hardcoded fallbacks (DRY principle).
"""

from pydantic import BaseModel
from streamlit import error, header, info, warning

from app.data_models.app_models import ChatConfig
from app.utils.error_messages import invalid_type
from app.utils.log import logger
from gui.components.prompts import render_prompt_editor
from gui.config.text import PROMPTS_HEADER


def render_prompts(chat_config: ChatConfig | BaseModel):  # -> dict[str, str]:
    """
    Render and edit the prompt configuration for agent roles in the Streamlit UI.

    Loads prompts directly from ChatConfig.prompts without hardcoded fallbacks.
    Follows DRY principle with config_chat.json as single source of truth.
    """

    header(PROMPTS_HEADER)
    # S8-F8.1: prominent warning — prompt edits are display-only and not persisted
    warning(
        "Edits on this page are display-only and will not be saved. "
        "To persist prompt changes, edit config_chat.json directly."
    )

    if not isinstance(chat_config, ChatConfig):
        msg = invalid_type("ChatConfig", type(chat_config).__name__)
        logger.error(msg)
        error(msg)
        return None

    # Load prompts directly from ChatConfig - single source of truth
    prompts = chat_config.prompts

    if not prompts:
        info("No prompts configured. Add prompts to config_chat.json.")
        return None

    updated_prompts = prompts.copy()

    # Edit prompts
    for prompt_key, prompt_value in prompts.items():
        new_value = render_prompt_editor(prompt_key, prompt_value, height=200)
        if new_value != prompt_value and new_value is not None:
            updated_prompts[prompt_key] = new_value

    # Note: Changes are display-only, not persisted (YAGNI principle)
