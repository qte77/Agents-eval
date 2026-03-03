from streamlit import header, info, markdown

from gui.config.text import HOME_DESCRIPTION, HOME_HEADER, HOME_INFO, ONBOARDING_STEPS


def render_home():
    header(HOME_HEADER)
    markdown(HOME_DESCRIPTION)
    # S8-F8.1: correct onboarding order — Settings before App
    info(HOME_INFO)
    # STORY-008: step-by-step onboarding guide
    for step in ONBOARDING_STEPS:
        markdown(f"**{step['title']}**\n\n{step['description']}")
