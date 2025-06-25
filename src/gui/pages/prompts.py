from streamlit import header, warning

from gui.components.prompts import render_prompt_editor
from gui.utils.config import PROMPTS_DEFAULT
from gui.utils.text import PROMPTS_HEADER, PROMPTS_WARNING


def render_prompts(prompts: dict[str, str]) -> dict[str, str]:
    header(PROMPTS_HEADER)

    updated = False

    if not prompts:
        warning(PROMPTS_WARNING)
        prompts = PROMPTS_DEFAULT

    updated_prompts = prompts.copy()

    # Edit prompts
    for prompt_key, prompt_value in prompts.items():
        new_value = render_prompt_editor(prompt_key, prompt_value, height=200)
        if new_value != prompt_value and new_value is not None:
            updated_prompts[prompt_key] = new_value
            updated = True

    return updated_prompts if updated else prompts
