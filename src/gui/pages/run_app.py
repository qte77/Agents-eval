from streamlit import button, header, info, text_input, warning

from app.main import main

from ..components.output import render_output


async def render_app(provider: str | None = None):
    header("Run Research Query")
    if provider is None:
        provider = text_input("Provider?")
    query = text_input("What would you like to research?")

    if button("Run Query"):
        if query:
            info(f"Running query: {query}")
            try:
                result = await main(provider=provider, query=query)
                render_output(result)
            except Exception as e:
                warning(e)
                print(e)
        else:
            warning("Please enter a query")
    else:
        render_output("Run the agent to see results here")
