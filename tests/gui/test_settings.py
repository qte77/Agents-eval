"""
Tests for STORY-011: selectbox dropdowns in _render_tier2_llm_judge().

Verifies that:
- tier2_provider uses selectbox with PROVIDER_REGISTRY keys + "auto"
- tier2_fallback_provider uses selectbox with PROVIDER_REGISTRY keys (no "auto")
- tier2_model uses selectbox populated from ChatConfig
- tier2_fallback_model uses selectbox populated from ChatConfig
- fallback_strategy uses selectbox with "tier1_only" option
- Judge Settings expanders use expanded=False
"""

from unittest.mock import MagicMock, patch

from app.data_models.app_models import PROVIDER_REGISTRY
from app.judge.settings import JudgeSettings
from app.common.settings import CommonSettings


def _make_session_state_mock(initial: dict | None = None) -> MagicMock:
    """Create a MagicMock that behaves like st.session_state for dict-like access."""
    data = dict(initial or {})
    mock = MagicMock()
    mock.__getitem__ = lambda self, k: data[k]
    mock.__setitem__ = lambda self, k, v: data.__setitem__(k, v)
    mock.__delitem__ = lambda self, k: data.__delitem__(k)
    mock.__contains__ = lambda self, k: k in data
    mock.keys = lambda: data.keys()
    mock.items = lambda: data.items()
    mock.get = lambda k, default=None: data.get(k, default)
    mock._data = data
    return mock


class TestTier2ProviderSelectbox:
    """Tests that tier2_provider uses selectbox with correct options."""

    def test_tier2_provider_uses_selectbox_not_text_input(self):
        """Test that tier2_provider field uses selectbox, not text_input."""
        mock_session = _make_session_state_mock()
        mock_selectbox = MagicMock(return_value="openai")
        mock_text_input = MagicMock(return_value="")

        with (
            patch("gui.pages.settings.selectbox", mock_selectbox),
            patch("gui.pages.settings.text_input", mock_text_input),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.expander"),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        # selectbox must be called for Provider (not text_input)
        provider_selectbox_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Provider" in str(call.args[0])
            and "Fallback" not in str(call.args[0])
        ]
        assert len(provider_selectbox_calls) >= 1, (
            "selectbox must be called for tier2_provider (not text_input)"
        )

        # text_input must NOT be called for Provider (non-fallback)
        provider_text_input_calls = [
            call
            for call in mock_text_input.call_args_list
            if call.args and call.args[0] == "Provider"
        ]
        assert len(provider_text_input_calls) == 0, (
            "text_input must NOT be used for tier2_provider"
        )

    def test_tier2_provider_selectbox_includes_registry_keys_and_auto(self):
        """Test that tier2_provider selectbox options include all PROVIDER_REGISTRY keys + 'auto'."""
        mock_session = _make_session_state_mock()
        mock_selectbox = MagicMock(return_value="auto")

        with (
            patch("gui.pages.settings.selectbox", mock_selectbox),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.expander"),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        # Find the selectbox call for tier2_provider (not fallback)
        provider_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Provider" in str(call.args[0])
            and "Fallback" not in str(call.args[0])
        ]
        assert len(provider_calls) >= 1, "selectbox must be called for tier2_provider"
        call_kwargs = provider_calls[0].kwargs
        options = call_kwargs.get("options", [])
        expected_keys = list(PROVIDER_REGISTRY.keys())
        for key in expected_keys:
            assert key in options, f"PROVIDER_REGISTRY key '{key}' missing from tier2_provider options"
        assert "auto" in options, "'auto' must be in tier2_provider options"


class TestTier2FallbackProviderSelectbox:
    """Tests that tier2_fallback_provider uses selectbox without 'auto'."""

    def test_tier2_fallback_provider_uses_selectbox(self):
        """Test that tier2_fallback_provider field uses selectbox, not text_input."""
        mock_session = _make_session_state_mock()
        mock_selectbox = MagicMock(return_value="github")
        mock_text_input = MagicMock(return_value="")

        with (
            patch("gui.pages.settings.selectbox", mock_selectbox),
            patch("gui.pages.settings.text_input", mock_text_input),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.expander"),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        fallback_provider_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Fallback Provider" in str(call.args[0])
        ]
        assert len(fallback_provider_calls) >= 1, (
            "selectbox must be called for tier2_fallback_provider"
        )

        # text_input must NOT be called for Fallback Provider
        fallback_text_input_calls = [
            call
            for call in mock_text_input.call_args_list
            if call.args and "Fallback Provider" in str(call.args[0])
        ]
        assert len(fallback_text_input_calls) == 0, (
            "text_input must NOT be used for tier2_fallback_provider"
        )

    def test_tier2_fallback_provider_selectbox_excludes_auto(self):
        """Test that tier2_fallback_provider options include registry keys but NOT 'auto'."""
        mock_session = _make_session_state_mock()
        mock_selectbox = MagicMock(return_value="github")

        with (
            patch("gui.pages.settings.selectbox", mock_selectbox),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.expander"),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        fallback_provider_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Fallback Provider" in str(call.args[0])
        ]
        assert len(fallback_provider_calls) >= 1
        call_kwargs = fallback_provider_calls[0].kwargs
        options = call_kwargs.get("options", [])
        expected_keys = list(PROVIDER_REGISTRY.keys())
        for key in expected_keys:
            assert key in options, (
                f"PROVIDER_REGISTRY key '{key}' missing from fallback provider options"
            )
        assert "auto" not in options, "'auto' must NOT be in tier2_fallback_provider options"


class TestTier2ModelSelectbox:
    """Tests that tier2_model and tier2_fallback_model use selectbox."""

    def test_tier2_model_uses_selectbox_not_text_input(self):
        """Test that tier2_model field uses selectbox, not text_input."""
        mock_session = _make_session_state_mock()
        mock_selectbox = MagicMock(return_value="gpt-4o-mini")
        mock_text_input = MagicMock(return_value="")

        with (
            patch("gui.pages.settings.selectbox", mock_selectbox),
            patch("gui.pages.settings.text_input", mock_text_input),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.expander"),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        # Model selectbox should be called (not text_input) for "Model" (non-fallback)
        model_selectbox_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and call.args[0] == "Model"
        ]
        assert len(model_selectbox_calls) >= 1, (
            "selectbox must be called for tier2_model (not text_input)"
        )

        model_text_input_calls = [
            call
            for call in mock_text_input.call_args_list
            if call.args and call.args[0] == "Model"
        ]
        assert len(model_text_input_calls) == 0, "text_input must NOT be used for tier2_model"

    def test_tier2_fallback_model_uses_selectbox_not_text_input(self):
        """Test that tier2_fallback_model field uses selectbox, not text_input."""
        mock_session = _make_session_state_mock()
        mock_selectbox = MagicMock(return_value="gpt-4o-mini")
        mock_text_input = MagicMock(return_value="")

        with (
            patch("gui.pages.settings.selectbox", mock_selectbox),
            patch("gui.pages.settings.text_input", mock_text_input),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.expander"),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        fallback_model_selectbox_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Fallback Model" in str(call.args[0])
        ]
        assert len(fallback_model_selectbox_calls) >= 1, (
            "selectbox must be called for tier2_fallback_model"
        )

        fallback_model_text_input_calls = [
            call
            for call in mock_text_input.call_args_list
            if call.args and "Fallback Model" in str(call.args[0])
        ]
        assert len(fallback_model_text_input_calls) == 0, (
            "text_input must NOT be used for tier2_fallback_model"
        )


class TestFallbackStrategySelectbox:
    """Tests that fallback_strategy uses selectbox with 'tier1_only' option."""

    def test_fallback_strategy_selectbox_includes_tier1_only(self):
        """Test that fallback_strategy selectbox includes 'tier1_only' option."""
        mock_session = _make_session_state_mock()
        mock_selectbox = MagicMock(return_value="tier1_only")

        with (
            patch("gui.pages.settings.selectbox", mock_selectbox),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.expander"),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        fallback_strategy_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Fallback Strategy" in str(call.args[0])
        ]
        assert len(fallback_strategy_calls) >= 1, (
            "selectbox must be called for fallback_strategy"
        )
        call_kwargs = fallback_strategy_calls[0].kwargs
        options = call_kwargs.get("options", [])
        assert "tier1_only" in options, "'tier1_only' must be in fallback_strategy options"


class TestJudgeSettingsExpanderCollapsed:
    """Tests that judge settings expanders use expanded=False."""

    def _collect_expander_calls(self, mock_expander: MagicMock) -> list:
        """Helper to collect judge settings expander calls."""
        return [
            call
            for call in mock_expander.call_args_list
            if call.args and "Judge Settings" in str(call.args[0])
        ]

    def test_tier_configuration_expander_is_collapsed(self):
        """Test that Judge Settings - Tier Configuration expander uses expanded=False."""
        mock_session = _make_session_state_mock()
        mock_expander = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=None)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("gui.pages.settings.expander", mock_expander),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.selectbox", return_value="INFO"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier_configuration

            _render_tier_configuration(JudgeSettings())

        judge_calls = self._collect_expander_calls(mock_expander)
        assert len(judge_calls) >= 1, "expander must be called for Tier Configuration"
        for call in judge_calls:
            expanded = call.kwargs.get("expanded", True)
            assert expanded is False, (
                f"Judge Settings - Tier Configuration expander must use expanded=False, got {expanded}"
            )

    def test_composite_scoring_expander_is_collapsed(self):
        """Test that Judge Settings - Composite Scoring expander uses expanded=False."""
        mock_session = _make_session_state_mock()
        mock_expander = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=None)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("gui.pages.settings.expander", mock_expander),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.selectbox", return_value="INFO"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_composite_scoring

            _render_composite_scoring(JudgeSettings())

        judge_calls = self._collect_expander_calls(mock_expander)
        assert len(judge_calls) >= 1, "expander must be called for Composite Scoring"
        for call in judge_calls:
            expanded = call.kwargs.get("expanded", True)
            assert expanded is False, (
                f"Judge Settings - Composite Scoring expander must use expanded=False, got {expanded}"
            )

    def test_tier2_llm_judge_expander_is_collapsed(self):
        """Test that Judge Settings - Tier 2 LLM Judge expander uses expanded=False."""
        mock_session = _make_session_state_mock()
        mock_expander = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=None)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("gui.pages.settings.expander", mock_expander),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.selectbox", return_value="openai"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_tier2_llm_judge

            _render_tier2_llm_judge(JudgeSettings())

        judge_calls = self._collect_expander_calls(mock_expander)
        assert len(judge_calls) >= 1, "expander must be called for Tier 2 LLM Judge"
        for call in judge_calls:
            expanded = call.kwargs.get("expanded", True)
            assert expanded is False, (
                f"Judge Settings - Tier 2 LLM Judge expander must use expanded=False, got {expanded}"
            )

    def test_observability_expander_is_collapsed(self):
        """Test that Judge Settings - Observability expander uses expanded=False."""
        mock_session = _make_session_state_mock()
        mock_expander = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=None)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("gui.pages.settings.expander", mock_expander),
            patch("streamlit.session_state", mock_session),
            patch("gui.pages.settings.st.session_state", mock_session),
            patch("gui.pages.settings.header"),
            patch("gui.pages.settings.text"),
            patch("gui.pages.settings.selectbox", return_value="INFO"),
            patch("gui.pages.settings.checkbox", return_value=False),
            patch("gui.pages.settings.number_input", return_value=1.0),
            patch("gui.pages.settings.button", return_value=False),
            patch("gui.pages.settings.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import _render_observability_settings

            _render_observability_settings(JudgeSettings())

        judge_calls = self._collect_expander_calls(mock_expander)
        assert len(judge_calls) >= 1, "expander must be called for Observability"
        for call in judge_calls:
            expanded = call.kwargs.get("expanded", True)
            assert expanded is False, (
                f"Judge Settings - Observability expander must use expanded=False, got {expanded}"
            )
