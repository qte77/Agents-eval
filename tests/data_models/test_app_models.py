"""
Tests for AgentConfig.tools field typing (STORY-007).

Verifies that the tools field is annotated as list[Tool[Any]] rather than
list[Any], that the FIXME comment is removed, and that Pydantic schema
generation still works without PydanticSchemaGenerationError.
"""

import pytest
from pydantic import BaseModel, ValidationError
from pydantic_ai.models.test import TestModel as PydanticTestModel
from pydantic_ai.tools import Tool

from app.data_models.app_models import AgentConfig


@pytest.fixture()
def test_model() -> PydanticTestModel:
    """Return a PydanticAI TestModel for use in AgentConfig instances."""
    return PydanticTestModel()


class TestAgentConfigToolsAnnotation:
    """Verify the tools field annotation is list[Tool[Any]], not list[Any]."""

    def test_tools_field_annotation_is_tool_list(self):
        """AC1: tools field annotation must be list[Tool[Any]], not list[Any]."""
        from typing import get_args, get_origin

        tools_field = AgentConfig.model_fields["tools"]
        annotation = tools_field.annotation

        # Should not be list[Any] (the old annotation)
        origin = get_origin(annotation)
        args = get_args(annotation)
        assert origin is list, f"Expected list origin, got {origin}"
        # The inner type must not be plain Any
        assert len(args) == 1, f"Expected 1 type arg, got {args}"
        inner = args[0]
        # Tool[Any] has __origin__ = Tool; plain Any has no __origin__
        inner_origin = get_origin(inner)
        assert inner_origin is Tool or inner is Tool, (
            f"Expected Tool as inner type, got {inner}. "
            "tools field must be list[Tool[Any]], not list[Any]."
        )

    def test_fixme_comment_removed(self):
        """AC2: The FIXME comment on line 105 must be removed from app_models.py."""
        import inspect

        import app.data_models.app_models as mod

        source = inspect.getsource(mod)
        assert "FIXME tools" not in source, (
            "FIXME comment about tools field must be removed from app_models.py"
        )


class TestAgentConfigSchemaGeneration:
    """AC3: Pydantic schema generation must not raise PydanticSchemaGenerationError."""

    def test_model_fields_accessible(self):
        """AgentConfig.model_fields must be accessible without error."""
        fields = AgentConfig.model_fields
        assert "tools" in fields

    def test_model_validate_with_empty_tools(self, test_model):
        """AgentConfig.model_validate must work with an empty tools list."""
        config = AgentConfig.model_validate(
            {
                "model": test_model,
                "output_type": BaseModel,
                "system_prompt": "test prompt",
                "tools": [],
            }
        )
        assert config.tools == []

    def test_model_validate_with_tool_instance(self, test_model):
        """AgentConfig.model_validate must accept a list of Tool instances."""

        async def my_tool(x: int) -> str:
            """A simple test tool."""
            return str(x)

        tool = Tool(my_tool)
        config = AgentConfig.model_validate(
            {
                "model": test_model,
                "output_type": BaseModel,
                "system_prompt": "test prompt",
                "tools": [tool],
            }
        )
        assert len(config.tools) == 1
        assert isinstance(config.tools[0], Tool)

    def test_model_validate_default_tools(self, test_model):
        """AgentConfig.model_validate with no tools key must default to empty list."""
        config = AgentConfig.model_validate(
            {
                "model": test_model,
                "output_type": BaseModel,
                "system_prompt": "test prompt",
            }
        )
        assert config.tools == []


class TestAgentConfigToolsValidation:
    """AC4: Validation rejects non-Tool callables at existing call sites."""

    def test_non_tool_callable_rejected(self, test_model):
        """Non-Tool callable must be rejected by validate_tools."""
        with pytest.raises(ValidationError, match="All tools must be Tool instances"):
            AgentConfig.model_validate(
                {
                    "model": test_model,
                    "output_type": BaseModel,
                    "system_prompt": "test prompt",
                    "tools": [lambda x: x],
                }
            )


class TestCreateOptionalAgentToolsType:
    """Verify _create_optional_agent propagates Tool[Any] typing."""

    def test_tools_param_typed_as_tool_any(self) -> None:
        """tools parameter should be list[Tool[Any]] | None, not list[Any] | None."""
        import inspect

        from app.agents.agent_system import _create_optional_agent

        sig = inspect.signature(_create_optional_agent)
        tools_param = sig.parameters["tools"]
        annotation_str = str(tools_param.annotation)
        assert "Tool" in annotation_str, (
            f"Expected list[Tool[Any]] | None but got {annotation_str}"
        )

    def test_plain_dict_rejected(self, test_model):
        """Plain dict in tools list must be rejected by validate_tools."""
        with pytest.raises(ValidationError, match="All tools must be Tool instances"):
            AgentConfig.model_validate(
                {
                    "model": test_model,
                    "output_type": BaseModel,
                    "system_prompt": "test prompt",
                    "tools": [{"name": "not_a_tool"}],
                }
            )

    def test_multiple_valid_tools_accepted(self, test_model):
        """Multiple Tool instances must all be accepted."""

        async def tool_a(x: int) -> str:
            """Tool A."""
            return str(x)

        async def tool_b(y: str) -> int:
            """Tool B."""
            return len(y)

        config = AgentConfig.model_validate(
            {
                "model": test_model,
                "output_type": BaseModel,
                "system_prompt": "test prompt",
                "tools": [Tool(tool_a), Tool(tool_b)],
            }
        )
        assert len(config.tools) == 2
        assert all(isinstance(t, Tool) for t in config.tools)
