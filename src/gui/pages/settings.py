from streamlit import header, selectbox

from app.config.data_models import ChatConfig
from gui.config.text import SETTINGS_HEADER, SETTINGS_PROVIDER_LABEL


def render_settings(chat_config: ChatConfig) -> str:
    header(SETTINGS_HEADER)

    # updated = False
    # updated_config = config.copy()

    provider = selectbox(
        SETTINGS_PROVIDER_LABEL,
        chat_config.providers,
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
