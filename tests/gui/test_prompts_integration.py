"""
Tests for GUI prompts integration with ChatConfig.

Verifies that the prompts page loads prompts directly from ChatConfig
without hardcoded fallbacks.
"""

import pytest


class TestPromptsIntegration:
    """Test suite for GUI prompts integration."""

    def test_prompts_default_removed_from_config(self):
        """Test that PROMPTS_DEFAULT is removed from gui/config/config.py."""
        # This test will fail until we remove PROMPTS_DEFAULT
        try:
            from gui.config.config import PROMPTS_DEFAULT  # noqa: F401

            # If import succeeds, the constant still exists - fail the test
            pytest.fail("PROMPTS_DEFAULT should be removed from gui/config/config.py")
        except ImportError:
            # Expected - PROMPTS_DEFAULT should not exist
            pass
        except AttributeError:
            # Also acceptable - module exists but PROMPTS_DEFAULT doesn't
            pass

    def test_render_prompts_does_not_use_prompts_default_fallback(self):
        """render_prompts must not reference PROMPTS_DEFAULT as a fallback.

        Behavioral: call render_prompts and verify it loads prompts from ChatConfig
        directly rather than falling back to a PROMPTS_DEFAULT constant.
        """
        from unittest.mock import MagicMock, patch

        from app.data_models.app_models import ChatConfig, ProviderConfig

        # Build minimal valid ChatConfig
        provider_cfg = ProviderConfig(
            model_name="gpt-4o-mini",
            base_url="http://localhost:8080",  # type: ignore[arg-type]
        )
        chat_config = ChatConfig(
            providers={"openai": provider_cfg},
            inference={"max_tokens": 1000},
            prompts={"manager": "Behavioral test prompt."},
        )

        from gui.pages import prompts as prompts_mod

        with (
            patch.object(prompts_mod, "header"),
            patch.object(prompts_mod, "warning"),
            patch.object(prompts_mod, "error"),
            patch.object(prompts_mod, "info"),
            patch("gui.pages.prompts.render_prompt_editor") as mock_editor,
        ):
            mock_editor.return_value = None
            prompts_mod.render_prompts(chat_config)

        # render_prompt_editor must have been called with the prompts from ChatConfig
        assert mock_editor.called, (
            "render_prompts must call render_prompt_editor with ChatConfig prompts"
        )
        called_keys = [call.args[0] for call in mock_editor.call_args_list]
        assert "manager" in called_keys, (
            "render_prompts must render the 'manager' prompt from ChatConfig"
        )

    def test_render_prompts_with_invalid_config_shows_error(self):
        """render_prompts must show an error when config is not a ChatConfig instance.

        Behavioral: call render_prompts with a non-ChatConfig object and verify
        st.error is called (no PROMPTS_DEFAULT fallback).
        """
        from unittest.mock import MagicMock, patch

        from gui.pages import prompts as prompts_mod

        with (
            patch.object(prompts_mod, "header"),
            patch.object(prompts_mod, "warning"),
            patch.object(prompts_mod, "error") as mock_error,
            patch.object(prompts_mod, "info"),
        ):
            prompts_mod.render_prompts(MagicMock())  # type: ignore[arg-type]

        assert mock_error.called, (
            "render_prompts must call st.error when given an invalid config type"
        )
