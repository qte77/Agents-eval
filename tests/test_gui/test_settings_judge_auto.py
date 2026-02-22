"""
Tests for STORY-013: Judge auto mode conditional settings display.

When tier2_provider is "auto", model/fallback controls must be hidden.
When tier2_provider is a specific provider, all controls must be shown.
Timeout controls remain visible regardless of provider selection.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.judge.settings import JudgeSettings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_mock_chat_config(provider: str = "openai", model: str = "gpt-4o-mini") -> MagicMock:
    """Return a minimal ChatConfig mock for the settings renderer."""
    provider_cfg = MagicMock()
    provider_cfg.model_name = model
    provider_cfg.usage_limits = 25000
    chat_config = MagicMock()
    chat_config.providers = {provider: provider_cfg}
    return chat_config


def _call_render_tier2(session_state: dict, provider: str = "openai") -> list[str]:
    """Call _render_tier2_llm_judge with the given session state dict.

    Returns a list of widget keys that were rendered (selectbox and number_input keys).
    """
    from gui.pages.settings import _render_tier2_llm_judge

    judge_settings = JudgeSettings(tier2_provider=provider)
    rendered_keys: list[str] = []

    def capture_selectbox(*args, **kwargs):  # noqa: ANN002
        rendered_keys.append(kwargs.get("key", ""))
        return kwargs.get("options", [""])[0]

    def capture_number_input(*args, **kwargs):  # noqa: ANN002
        rendered_keys.append(kwargs.get("key", ""))
        return kwargs.get("value", 0.0)

    mock_expander = MagicMock()
    mock_expander.__enter__ = MagicMock(return_value=None)
    mock_expander.__exit__ = MagicMock(return_value=False)

    chat_config = _build_mock_chat_config()

    with (
        patch("gui.pages.settings.st.session_state", session_state),
        patch("gui.pages.settings.selectbox", side_effect=capture_selectbox),
        patch("gui.pages.settings.number_input", side_effect=capture_number_input),
        patch("gui.pages.settings.expander", return_value=mock_expander),
        patch("gui.pages.settings.load_config", return_value=chat_config),
        patch("gui.pages.settings.resolve_config_path", return_value="/fake/path"),
    ):
        _render_tier2_llm_judge(judge_settings)

    return rendered_keys


# ---------------------------------------------------------------------------
# AC1: When tier2_provider is "auto", model/fallback controls are hidden
# ---------------------------------------------------------------------------


class TestAutoModeHidesControls:
    """AC1: When tier2_provider is 'auto', downstream controls must not be rendered."""

    def test_primary_model_selectbox_hidden_when_auto(self):
        """tier2_model_input selectbox must NOT be rendered when provider is auto."""
        session_state: dict = {"judge_tier2_provider": "auto"}
        keys = _call_render_tier2(session_state, provider="auto")
        assert "tier2_model_input" not in keys, (
            "Primary model selectbox should be hidden when tier2_provider is 'auto'"
        )

    def test_fallback_provider_hidden_when_auto(self):
        """tier2_fallback_provider_input must NOT be rendered when provider is auto."""
        session_state: dict = {"judge_tier2_provider": "auto"}
        keys = _call_render_tier2(session_state, provider="auto")
        assert "tier2_fallback_provider_input" not in keys, (
            "Fallback provider selectbox should be hidden when tier2_provider is 'auto'"
        )

    def test_fallback_model_hidden_when_auto(self):
        """tier2_fallback_model_input must NOT be rendered when provider is auto."""
        session_state: dict = {"judge_tier2_provider": "auto"}
        keys = _call_render_tier2(session_state, provider="auto")
        assert "tier2_fallback_model_input" not in keys, (
            "Fallback model selectbox should be hidden when tier2_provider is 'auto'"
        )

    def test_fallback_strategy_hidden_when_auto(self):
        """fallback_strategy_input must NOT be rendered when provider is auto."""
        session_state: dict = {"judge_tier2_provider": "auto"}
        keys = _call_render_tier2(session_state, provider="auto")
        assert "fallback_strategy_input" not in keys, (
            "Fallback strategy selectbox should be hidden when tier2_provider is 'auto'"
        )

    def test_primary_provider_selectbox_still_shown_when_auto(self):
        """tier2_provider_input selectbox MUST still be rendered when provider is auto.

        The user needs to see and change the provider selection.
        """
        session_state: dict = {"judge_tier2_provider": "auto"}
        keys = _call_render_tier2(session_state, provider="auto")
        assert "tier2_provider_input" in keys, (
            "Primary provider selectbox must remain visible when tier2_provider is 'auto'"
        )


# ---------------------------------------------------------------------------
# AC2: When provider is specific, all controls reappear
# ---------------------------------------------------------------------------


class TestSpecificProviderShowsControls:
    """AC2: When tier2_provider is a specific provider, all controls must be visible."""

    @pytest.mark.parametrize("provider", ["openai", "anthropic", "github", "cerebras"])
    def test_all_controls_visible_for_specific_provider(self, provider: str):
        """All downstream controls must be rendered when provider is not 'auto'."""
        session_state: dict = {"judge_tier2_provider": provider}
        keys = _call_render_tier2(session_state, provider=provider)

        expected = [
            "tier2_provider_input",
            "tier2_model_input",
            "tier2_fallback_provider_input",
            "tier2_fallback_model_input",
            "fallback_strategy_input",
        ]
        for key in expected:
            assert key in keys, (
                f"Control '{key}' should be rendered when tier2_provider is '{provider}'"
            )


# ---------------------------------------------------------------------------
# AC3: Timeout and cost budget always visible
# ---------------------------------------------------------------------------


class TestAlwaysVisibleControls:
    """AC3: Timeout control must be visible regardless of provider selection."""

    def test_timeout_visible_when_auto(self):
        """tier2_timeout_seconds_input must be rendered even when provider is auto."""
        session_state: dict = {"judge_tier2_provider": "auto"}
        keys = _call_render_tier2(session_state, provider="auto")
        assert "tier2_timeout_seconds_input" in keys, (
            "Timeout control must remain visible when tier2_provider is 'auto'"
        )

    def test_timeout_visible_for_specific_provider(self):
        """tier2_timeout_seconds_input must be rendered for specific providers."""
        session_state: dict = {"judge_tier2_provider": "openai"}
        keys = _call_render_tier2(session_state, provider="openai")
        assert "tier2_timeout_seconds_input" in keys, (
            "Timeout control must remain visible for specific provider"
        )


# ---------------------------------------------------------------------------
# AC4: Session state defaults are retained for hidden controls
# ---------------------------------------------------------------------------


class TestSessionStateRetainsDefaults:
    """AC4: Hidden controls must not clear session state values."""

    def test_session_state_defaults_not_cleared_when_auto(self):
        """When tier2_provider is 'auto', hidden fields retain their default values.

        _build_judge_settings_from_session in run_app.py reads session state
        directly. If keys are missing, JudgeSettings uses model defaults.
        This test verifies that switching to auto does not actively delete keys.
        """
        from gui.pages.run_app import _build_judge_settings_from_session

        # Pre-populate session state as if user previously set values
        preset_state: dict = {
            "judge_tier2_provider": "auto",
            "judge_tier2_model": "gpt-4o-mini",
            "judge_tier2_fallback_provider": "github",
            "judge_tier2_fallback_model": "gpt-4o-mini",
            "judge_fallback_strategy": "tier1_only",
            "judge_tier2_timeout_seconds": 30.0,
        }

        # _build_judge_settings_from_session must not raise even with auto + all keys set
        with patch("gui.pages.run_app.st.session_state", preset_state):
            result = _build_judge_settings_from_session()

        assert result is not None, "Should build JudgeSettings from session state"
        assert result.tier2_provider == "auto"
        # Values for hidden fields must still be present from preset state
        assert result.tier2_model == "gpt-4o-mini"
        assert result.tier2_fallback_provider == "github"

    def test_build_judge_settings_valid_when_auto_no_overrides(self):
        """JudgeSettings builds correctly when only tier2_provider=auto is in session state."""
        from gui.pages.run_app import _build_judge_settings_from_session

        # Only provider key set (hidden controls never written to session state)
        minimal_state: dict = {"judge_tier2_provider": "auto"}

        with patch("gui.pages.run_app.st.session_state", minimal_state):
            result = _build_judge_settings_from_session()

        assert result is not None
        assert result.tier2_provider == "auto"
        # Model fields fall back to JudgeSettings defaults
        assert result.tier2_model == JudgeSettings().tier2_model
        assert result.tier2_fallback_provider == JudgeSettings().tier2_fallback_provider
