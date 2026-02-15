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

    def test_render_prompts_no_longer_imports_prompts_default(self):
        """Test that render_prompts doesn't import PROMPTS_DEFAULT."""
        # Read the source file and verify no import of PROMPTS_DEFAULT
        from pathlib import Path

        prompts_file = Path("src/gui/pages/prompts.py")
        content = prompts_file.read_text()

        # This will fail until we remove the import
        assert "from gui.config.config import PROMPTS_DEFAULT" not in content, (
            "render_prompts should not import PROMPTS_DEFAULT"
        )

    def test_render_prompts_no_longer_uses_prompts_default_fallback(self):
        """Test that render_prompts doesn't use PROMPTS_DEFAULT as fallback."""
        from pathlib import Path

        prompts_file = Path("src/gui/pages/prompts.py")
        content = prompts_file.read_text()

        # This will fail until we remove the fallback usage
        assert "PROMPTS_DEFAULT" not in content, (
            "render_prompts should not reference PROMPTS_DEFAULT anywhere"
        )
