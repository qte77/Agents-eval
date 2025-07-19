"""
Streamlit settings UI for provider and agent configuration.

This module provides a function to render and edit agent system settings,
including provider selection and related options, within the Streamlit GUI.
It validates the input configuration and ensures correct typing before rendering.
"""

from streamlit import error, header, selectbox

from app.datamodels.app_models import BaseModel, ChatConfig
from app.utils.error_messages import invalid_type
from app.utils.log import logger
from gui.config.text import SETTINGS_HEADER, SETTINGS_PROVIDER_LABEL


def render_settings(chat_config: ChatConfig | BaseModel) -> str:
    """
    Render and edit agent system settings in the Streamlit UI.

    Displays a header and a selectbox for choosing the inference provider.
    Validates that the input is a ChatConfig instance and displays an error if not.
    """
    header(SETTINGS_HEADER)

    # updated = False
    # updated_config = config.copy()

    if not isinstance(chat_config, ChatConfig):
        msg = invalid_type("ChatConfig", type(chat_config).__name__)
        logger.error(msg)
        error(msg)
        return msg

    provider = selectbox(
        label=SETTINGS_PROVIDER_LABEL,
        options=chat_config.providers.keys(),
    )

    # Run options
    # col1, col2 = st.columns(2)
    # with col1:
    #     streamed_output = st.checkbox(
    #         "Stream Output", value=config.get("streamed_output", False)
    #     )
    # with col2:
    #     st.checkbox("Include Sources", value=True)  # include_sources

    # Allow adding new providers
    # new_provider = st.text_input("Add New Provider")
    # api_key = st.text_input(f"{provider} API Key", type="password")
    # if st.button("Add Provider") and new_provider and new_provider not in providers:
    #     providers.append(new_provider)
    #     updated_config["providers"] = providers
    #     updated_config["api_key"] = api_key
    #     updated = True
    #     st.success(f"Added provider: {new_provider}")

    # # Update config if changed
    # if (
    #     include_a != config.get("include_a", False)
    #     or include_b != config.get("include_b", False)
    #     or streamed_output != config.get("streamed_output", False)
    # ):
    #     updated_config["include_a"] = include_a
    #     updated_config["include_b"] = include_b
    #     updated_config["streamed_output"] = streamed_output
    #     updated = True

    return provider
