from src.main import main
from streamlit_gui.components.output import render_output
from streamlit import button, header, info, text_input, warning


async def render_app(config):
    header("Run Research Query")
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
