"""Tests for STORY-012: Type-aware output rendering.

Verifies that render_output() dispatches to appropriate Streamlit
widgets based on result type instead of using generic st.write().
"""

from unittest.mock import patch, MagicMock

import pytest
from pydantic import BaseModel


class SampleModel(BaseModel):
    """A minimal Pydantic model for testing."""

    name: str = "test"
    score: float = 0.5


class TestRenderOutputTypeDispatch:
    """Tests for type-aware rendering dispatch in render_output()."""

    @patch("gui.components.output.st")
    def test_dict_renders_via_st_json(self, mock_st: MagicMock) -> None:
        """Dict results should render via st.json(), not st.write()."""
        from gui.components.output import render_output

        data = {"key": "value", "nested": {"a": 1}}
        render_output(result=data)

        mock_st.json.assert_called_once_with(data, expanded=True)

    @patch("gui.components.output.st")
    def test_string_renders_via_st_markdown(self, mock_st: MagicMock) -> None:
        """String results should render via st.markdown()."""
        from gui.components.output import render_output

        text = "# Hello World"
        render_output(result=text)

        mock_st.markdown.assert_called_once_with(text)

    @patch("gui.components.output.st")
    def test_pydantic_model_renders_via_st_json_with_model_dump(
        self, mock_st: MagicMock
    ) -> None:
        """Pydantic BaseModel instances should render via st.json(model_dump())."""
        from gui.components.output import render_output

        model = SampleModel(name="test", score=0.8)
        render_output(result=model)

        mock_st.json.assert_called_once_with(
            model.model_dump(), expanded=True
        )

    @patch("gui.components.output.st")
    def test_none_result_shows_info_message(self, mock_st: MagicMock) -> None:
        """None/falsy results should display info message via st.info()."""
        from gui.components.output import render_output

        render_output(result=None, info_str="No results available")

        mock_st.info.assert_called_once_with("No results available")
