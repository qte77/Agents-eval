from streamlit import button, header, info, text_input, warning

from app.main import main
from app.utils.log import logger

from ..components.output import render_output
from ..utils.text import (
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

    if button(RUN_APP_BUTTON):
        if query:
            info(f"{RUN_APP_QUERY_RUN_INFO} {query}")
            try:
                result = await main(provider=provider, query=query)
                render_output(result)
            except Exception as e:
                warning(e)
                logger.exception(e)
        else:
            warning(RUN_APP_QUERY_WARNING)
    else:
        render_output(RUN_APP_OUTPUT_PLACEHOLDER)
