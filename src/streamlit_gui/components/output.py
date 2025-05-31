from typing import Any

from streamlit import empty, info, subheader


def render_output(result: Any = None, info_str: str = None, type: str = None):
    """
    Renders the output in a Streamlit app based on the provided type.

    Args:
        result (Any, optional): The content to be displayed. Can be JSON, code
            markdown, or plain text.
        info (str, optional): The information message to be displayed if result is None.
        type (str, optional): The type of the result content. Can be 'json', 'code',
            'md', or other for plain text.

    Returns:
        Out: None
    """

    subheader("Output")

    if result:
        output_container = empty()
        output_container.write(result)
        # match type:
        #     case "json":
        #         json(result)
        #     case "code":
        #         code(result)
        #     case "md":
        #         markdown(result)
        #     case _:
        #         text(result)
        #         # st.write(result)
    else:
        info_str(info)
