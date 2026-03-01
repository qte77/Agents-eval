"""Tests for STORY-008: Home page onboarding guide.

Covers:
- Onboarding step constants exist in text.py
- render_home() renders numbered step-by-step content
- Steps reference Settings and App pages
- Onboarding content comes from text.py constants, not inline strings

Mock strategy:
- Patch streamlit functions to capture rendered output
- Direct import of text.py constants for structure validation
"""

from unittest.mock import patch


class TestOnboardingConstants:
    """Verify text.py exports onboarding step constants."""

    def test_onboarding_steps_exists_in_text(self) -> None:
        """text.py must export ONBOARDING_STEPS."""
        from gui.config import text

        assert hasattr(text, "ONBOARDING_STEPS"), "text.py must define ONBOARDING_STEPS constant"

    def test_onboarding_steps_is_list_with_items(self) -> None:
        """ONBOARDING_STEPS must be a non-empty list."""
        from gui.config.text import ONBOARDING_STEPS

        assert isinstance(ONBOARDING_STEPS, list), "ONBOARDING_STEPS must be a list"
        assert len(ONBOARDING_STEPS) >= 3, "ONBOARDING_STEPS must have at least 3 steps"

    def test_onboarding_steps_have_title_and_description(self) -> None:
        """Each step must have 'title' and 'description' keys."""
        from gui.config.text import ONBOARDING_STEPS

        for i, step in enumerate(ONBOARDING_STEPS):
            assert "title" in step, f"Step {i} must have a 'title' key"
            assert "description" in step, f"Step {i} must have a 'description' key"

    def test_onboarding_steps_reference_settings(self) -> None:
        """At least one step must reference Settings page."""
        from gui.config.text import ONBOARDING_STEPS

        all_text = " ".join(s["title"] + " " + s["description"] for s in ONBOARDING_STEPS)
        assert "Settings" in all_text, "ONBOARDING_STEPS must reference Settings page"

    def test_onboarding_steps_reference_app(self) -> None:
        """At least one step must reference App page."""
        from gui.config.text import ONBOARDING_STEPS

        all_text = " ".join(s["title"] + " " + s["description"] for s in ONBOARDING_STEPS)
        assert "App" in all_text, "ONBOARDING_STEPS must reference App page"


class TestRenderHomeOnboarding:
    """Verify render_home() renders the onboarding steps."""

    def test_render_home_renders_numbered_steps(self) -> None:
        """render_home must render numbered step content via st.markdown."""
        from gui.pages.home import render_home

        with (
            patch("gui.pages.home.header"),
            patch("gui.pages.home.markdown") as mock_md,
            patch("gui.pages.home.info"),
        ):
            render_home()

        all_md = " ".join(str(call.args[0]) for call in mock_md.call_args_list if call.args)
        assert "1." in all_md or "1)" in all_md, (
            f"render_home must render numbered steps. Got markdown: {all_md[:300]}"
        )

    def test_render_home_uses_text_constants_not_inline(self) -> None:
        """render_home must import onboarding content from text.py."""
        import inspect

        from gui.pages.home import render_home

        source = inspect.getsource(render_home)
        # Should not contain hardcoded step strings
        assert "Configure Provider" not in source, (
            "render_home must not contain inline onboarding strings — use text.py constants"
        )

    def test_render_home_renders_settings_and_app_references(self) -> None:
        """Rendered onboarding must mention Settings and App."""
        from gui.pages.home import render_home

        with (
            patch("gui.pages.home.header"),
            patch("gui.pages.home.markdown") as mock_md,
            patch("gui.pages.home.info"),
        ):
            render_home()

        all_md = " ".join(str(call.args[0]) for call in mock_md.call_args_list if call.args)
        assert "Settings" in all_md, "Onboarding must reference Settings page"
        assert "App" in all_md, "Onboarding must reference App page"
