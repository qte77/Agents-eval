from streamlit import button, exception, header, info, subheader, text_input, warning

from app.main import main
from app.utils.log import logger
from gui.components.output import render_output
from gui.config.text import (
    OUTPUT_SUBHEADER,
    RUN_APP_BUTTON,
    RUN_APP_HEADER,
    RUN_APP_OUTPUT_PLACEHOLDER,
    RUN_APP_PROVIDER_PLACEHOLDER,
    RUN_APP_QUERY_PLACEHOLDER,
    RUN_APP_QUERY_RUN_INFO,
    RUN_APP_QUERY_WARNING,
)


async def render_app(provider: str | None = None):
    header(RUN_APP_HEADER)
    if provider is None:
        provider = text_input(RUN_APP_PROVIDER_PLACEHOLDER)
    query = text_input(RUN_APP_QUERY_PLACEHOLDER)

    subheader(OUTPUT_SUBHEADER)
    if button(RUN_APP_BUTTON):
        if query:
            info(f"{RUN_APP_QUERY_RUN_INFO} {query}")
            try:
                result = await main(chat_provider=provider, query=query)
                render_output(result)
            except Exception as e:
                render_output(None)
                exception(e)
                logger.exception(e)
        else:
            warning(RUN_APP_QUERY_WARNING)
    else:
        render_output(RUN_APP_OUTPUT_PLACEHOLDER)
