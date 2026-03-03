"""Output rendering component with type-aware dispatch.

Renders results using appropriate Streamlit widgets based on the
result type: st.json() for dicts and Pydantic models, st.markdown()
for strings, and st.write() as a fallback.
"""

from typing import Any, cast

import streamlit as st
from pydantic import BaseModel


def render_output(
    result: Any = None,
    info_str: str | None = None,
    output_type: str | None = None,
) -> None:
    """Renders output using type-appropriate Streamlit widgets.

    Args:
        result (Any, optional): The content to be displayed. Dispatches to
            st.json() for dicts/Pydantic models, st.markdown() for strings,
            st.write() for other types.
        info_str (str, optional): Info message displayed when result is None/falsy.
        output_type (str, optional): The type hint for the result content.
    """
    if result:
        if isinstance(result, BaseModel):
            st.json(result.model_dump(), expanded=True)
        elif isinstance(result, dict):
            st.json(cast(dict[str, Any], result), expanded=True)
        elif isinstance(result, str):
            st.markdown(result)
        else:
            output_container = st.empty()
            output_container.write(result)
    else:
        st.info(info_str)
