"""
Tests for STORY-012: Standalone a11y/usability fixes for the GUI.

Covers:
- styling.py: CSS radio button circle hiding hack removed (WCAG 1.3.3, 1.4.1)
- log_capture.py: text-prefix badges ([WARN], [ERR], [INFO], [DBG]) added (WCAG 1.4.1)
- log_capture.py: module text color #999999 -> #696969 contrast fix (WCAG 1.4.3)
- run_gui.py: include_researcher and include_analyst default to True
- sidebar.py: radio label is "Navigation" not " " (WCAG 1.3.1, 2.4.6)
- sidebar.py: Phoenix link includes "(opens in new tab)" warning (WCAG 3.2.5)
- text.py: HOME_INFO mentions Settings before App (correct onboarding order)
- text.py: RUN_APP_QUERY_PLACEHOLDER is domain-specific
- prompts.py: display-only warning is shown prominently

Mock strategy:
- No real Streamlit runtime needed
- Behavioral: mock injection for CSS checks, HTML output for color checks
- Direct function calls with patched streamlit for all assertions
"""

import importlib
from unittest.mock import patch

# ---------------------------------------------------------------------------
# 1. styling.py — CSS radio button circle hiding hack must be removed
# ---------------------------------------------------------------------------


class TestStylingRadioHackRemoved:
    """Verify the radio circle hiding CSS hack is not in styling.py.

    WCAG 1.3.3, 1.4.1: Native selection indicators must not be hidden via CSS.
    """

    def test_radio_circle_css_hack_not_in_styling_source(self) -> None:
        """add_custom_styling must not inject CSS that hides radio button circles.

        Behavioral: patch st.markdown/st.html and verify no 'display: none'
        CSS targeting radio elements is passed.
        """
        from gui.config import styling as styling_mod

        with (
            patch("streamlit.set_page_config"),
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.html") as mock_html,
        ):
            styling_mod.add_custom_styling("Test")

        # Collect all CSS injected via markdown or html calls
        all_css_injected = " ".join(
            str(arg)
            for call in (mock_md.call_args_list + mock_html.call_args_list)
            for arg in call.args
        )
        assert "display: none" not in all_css_injected, (
            "add_custom_styling must not hide native radio button circles via 'display: none'"
        )

    def test_radio_circle_css_hack_not_contain_radiogroup_hide(self) -> None:
        """add_custom_styling must not inject radiogroup-targeting hide CSS."""
        from gui.config import styling as styling_mod

        with (
            patch("streamlit.set_page_config"),
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.html") as mock_html,
        ):
            styling_mod.add_custom_styling("Test")

        all_css_injected = " ".join(
            str(arg)
            for call in (mock_md.call_args_list + mock_html.call_args_list)
            for arg in call.args
        )
        # radiogroup + display:none combination must not be present
        assert (
            "radiogroup" not in all_css_injected.lower() or "display: none" not in all_css_injected
        ), "Radio group elements must not be hidden via injected CSS"


# ---------------------------------------------------------------------------
# 2. log_capture.py — text-prefix badges required
# ---------------------------------------------------------------------------


class TestLogCaptureTextBadges:
    """Verify that format_logs_as_html includes text-prefix badges for log levels.

    WCAG 1.4.1: Information must not be conveyed by color alone.
    Text badges like [WARN], [ERR], [INFO], [DBG] are required.
    """

    def test_format_logs_as_html_includes_text_badge_for_warning(self) -> None:
        """HTML output for WARNING level must include a text badge like [WARN] or [WARNING]."""
        from gui.utils.log_capture import LogCapture

        logs = [
            {
                "timestamp": "2026-01-01 12:00:00",
                "level": "WARNING",
                "module": "app.test",
                "message": "Something might be wrong",
            }
        ]
        html = LogCapture.format_logs_as_html(logs)
        # Must contain a visible text badge, not just color
        assert "[WARN" in html or "[WARNING]" in html, (
            f"HTML must include text badge for WARNING level, got: {html[:300]}"
        )

    def test_format_logs_as_html_includes_text_badge_for_error(self) -> None:
        """HTML output for ERROR level must include a text badge like [ERR] or [ERROR]."""
        from gui.utils.log_capture import LogCapture

        logs = [
            {
                "timestamp": "2026-01-01 12:00:00",
                "level": "ERROR",
                "module": "app.test",
                "message": "Something broke",
            }
        ]
        html = LogCapture.format_logs_as_html(logs)
        assert "[ERR" in html or "[ERROR]" in html, (
            f"HTML must include text badge for ERROR level, got: {html[:300]}"
        )

    def test_format_logs_as_html_includes_text_badge_for_info(self) -> None:
        """HTML output for INFO level must include a text badge like [INFO]."""
        from gui.utils.log_capture import LogCapture

        logs = [
            {
                "timestamp": "2026-01-01 12:00:00",
                "level": "INFO",
                "module": "app.test",
                "message": "Informational message",
            }
        ]
        html = LogCapture.format_logs_as_html(logs)
        assert "[INFO]" in html, f"HTML must include text badge for INFO level, got: {html[:300]}"

    def test_format_logs_as_html_includes_text_badge_for_debug(self) -> None:
        """HTML output for DEBUG level must include a text badge like [DBG] or [DEBUG]."""
        from gui.utils.log_capture import LogCapture

        logs = [
            {
                "timestamp": "2026-01-01 12:00:00",
                "level": "DEBUG",
                "module": "app.test",
                "message": "Debug information",
            }
        ]
        html = LogCapture.format_logs_as_html(logs)
        assert "[DBG" in html or "[DEBUG]" in html, (
            f"HTML must include text badge for DEBUG level, got: {html[:300]}"
        )


# ---------------------------------------------------------------------------
# 3. log_capture.py — module text color must be #696969 not #999999
# ---------------------------------------------------------------------------


class TestLogCaptureModuleColorContrast:
    """Verify the module text color meets WCAG 1.4.3 contrast requirements.

    #999999 has contrast ratio 2.8:1 (fails AA).
    #696969 has contrast ratio 5.9:1 (passes AA).
    """

    def test_log_capture_html_does_not_use_low_contrast_color(self) -> None:
        """format_logs_as_html must not render #999999 for module text color."""
        from gui.utils.log_capture import LogCapture

        logs = [
            {
                "timestamp": "2026-01-01 12:00:00",
                "level": "INFO",
                "module": "app.test",
                "message": "Color contrast check",
            }
        ]
        html = LogCapture.format_logs_as_html(logs)
        assert "#999999" not in html, (
            "format_logs_as_html must not use #999999 (contrast 2.8:1 fails WCAG 1.4.3). "
            "Use #696969 (contrast 5.9:1) instead."
        )

    def test_log_capture_html_uses_accessible_color(self) -> None:
        """format_logs_as_html must render #696969 for module text color (WCAG 1.4.3)."""
        from gui.utils.log_capture import LogCapture

        logs = [
            {
                "timestamp": "2026-01-01 12:00:00",
                "level": "INFO",
                "module": "app.test",
                "message": "Color contrast check",
            }
        ]
        html = LogCapture.format_logs_as_html(logs)
        assert "#696969" in html, (
            "format_logs_as_html must use #696969 for module text color (contrast 5.9:1, WCAG AA)."
        )


# ---------------------------------------------------------------------------
# 4. run_gui.py — default sub-agents must be True
# ---------------------------------------------------------------------------


class TestRunGuiSubAgentDefaults:
    """Verify get_session_state_defaults returns True for researcher and analyst.

    S8-F8.1: default sub-agents to True for better UX.
    Mock strategy: patch load_config during reload to isolate module-level config
    loading from JSON parse errors in config_chat.json.
    """

    def test_get_session_state_defaults_include_researcher_is_true(self) -> None:
        """get_session_state_defaults must return include_researcher=True."""
        # Patch load_config during reload to avoid module-level JSON parse errors
        with patch("app.utils.load_configs.load_config"):
            import run_gui

            importlib.reload(run_gui)
        defaults = run_gui.get_session_state_defaults()
        assert defaults["include_researcher"] is True, (
            f"Expected include_researcher=True, got {defaults['include_researcher']}"
        )

    def test_get_session_state_defaults_include_analyst_is_true(self) -> None:
        """get_session_state_defaults must return include_analyst=True."""
        with patch("app.utils.load_configs.load_config"):
            import run_gui

            importlib.reload(run_gui)
        defaults = run_gui.get_session_state_defaults()
        assert defaults["include_analyst"] is True, (
            f"Expected include_analyst=True, got {defaults['include_analyst']}"
        )

    def test_get_session_state_defaults_include_synthesiser_stays_false(self) -> None:
        """get_session_state_defaults must keep include_synthesiser=False (not changed by AC)."""
        with patch("app.utils.load_configs.load_config"):
            import run_gui

            importlib.reload(run_gui)
        defaults = run_gui.get_session_state_defaults()
        assert defaults["include_synthesiser"] is False, (
            f"Expected include_synthesiser=False, got {defaults['include_synthesiser']}"
        )


# ---------------------------------------------------------------------------
# 5. sidebar.py — radio label must be "Navigation" not " "
# ---------------------------------------------------------------------------


class TestSidebarRadioLabel:
    """Verify sidebar.py uses "Navigation" as radio label with label_visibility="collapsed".

    WCAG 1.3.1, 2.4.6: Labels must be meaningful and descriptive.
    """

    def _make_mock_sidebar(self):
        """Create a MagicMock sidebar with a radio that returns 'Home'."""
        from unittest.mock import MagicMock

        mock_sb = MagicMock()
        mock_sb.radio = MagicMock(return_value="Home")
        mock_sb.title = MagicMock()
        mock_sb.divider = MagicMock()
        mock_sb.markdown = MagicMock()
        mock_sb.caption = MagicMock()
        mock_sb.info = MagicMock()
        return mock_sb

    def test_sidebar_uses_navigation_label(self) -> None:
        """render_sidebar must call sidebar.radio with 'Navigation' as the label."""
        from unittest.mock import patch

        from gui.components.sidebar import render_sidebar

        mock_sb = self._make_mock_sidebar()
        with patch("gui.components.sidebar.sidebar", mock_sb):
            render_sidebar("Test App")

        radio_calls = mock_sb.radio.call_args_list
        assert radio_calls, "sidebar.radio must be called"
        first_arg = (
            radio_calls[0].args[0]
            if radio_calls[0].args
            else radio_calls[0].kwargs.get("label", "")
        )
        assert first_arg == "Navigation", (
            f"sidebar.radio must use 'Navigation' as label, got: {first_arg!r}"
        )

    def test_sidebar_does_not_use_space_only_label(self) -> None:
        """render_sidebar must not pass ' ' (space-only) as the radio label."""
        from unittest.mock import patch

        from gui.components.sidebar import render_sidebar

        mock_sb = self._make_mock_sidebar()
        with patch("gui.components.sidebar.sidebar", mock_sb):
            render_sidebar("Test App")

        radio_calls = mock_sb.radio.call_args_list
        for call in radio_calls:
            first_arg = call.args[0] if call.args else call.kwargs.get("label", "")
            assert first_arg != " ", (
                "sidebar.radio must not use ' ' (space) as label — use 'Navigation' instead."
            )

    def test_sidebar_uses_label_visibility_collapsed(self) -> None:
        """render_sidebar must call radio with label_visibility='collapsed'."""
        from unittest.mock import patch

        from gui.components.sidebar import render_sidebar

        mock_sb = self._make_mock_sidebar()
        with patch("gui.components.sidebar.sidebar", mock_sb):
            render_sidebar("Test App")

        radio_calls = mock_sb.radio.call_args_list
        assert radio_calls, "sidebar.radio must be called"
        kwargs = radio_calls[0].kwargs
        assert kwargs.get("label_visibility") == "collapsed", (
            f"sidebar.radio must use label_visibility='collapsed', got: {kwargs.get('label_visibility')!r}"
        )

    def test_sidebar_phoenix_link_warns_opens_in_new_tab(self) -> None:
        """render_sidebar Phoenix markdown must include '(opens in new tab)' text.

        S8-F8.1: Warn users that the link opens in a new tab (WCAG 3.2.5).
        """
        from unittest.mock import patch

        from gui.components.sidebar import render_sidebar

        mock_sb = self._make_mock_sidebar()
        with patch("gui.components.sidebar.sidebar", mock_sb):
            render_sidebar("Test App")

        markdown_calls = mock_sb.markdown.call_args_list
        all_markdown_content = " ".join(str(call.args[0]) for call in markdown_calls if call.args)
        assert "opens in new tab" in all_markdown_content, (
            "render_sidebar Phoenix link must include '(opens in new tab)' text for WCAG 3.2.5."
        )


# ---------------------------------------------------------------------------
# 6. text.py — onboarding order and domain-specific placeholder
# ---------------------------------------------------------------------------


class TestTextOnboardingContent:
    """Verify text.py contains correct onboarding order and domain-specific placeholder.

    S8-F8.1: Settings must come before App in onboarding instructions.
    """

    def test_home_info_mentions_settings_before_app(self) -> None:
        """HOME_INFO must mention 'Settings' before 'App' in the onboarding message."""
        from gui.config.text import HOME_INFO

        settings_pos = HOME_INFO.find("Settings")
        app_pos = HOME_INFO.find("App")

        assert settings_pos != -1, "HOME_INFO must mention 'Settings'"
        assert app_pos != -1, "HOME_INFO must mention 'App'"
        assert settings_pos < app_pos, (
            f"HOME_INFO must mention 'Settings' before 'App'. "
            f"Got: Settings at {settings_pos}, App at {app_pos}. "
            f"HOME_INFO={HOME_INFO!r}"
        )

    def test_run_app_query_placeholder_is_domain_specific(self) -> None:
        """RUN_APP_QUERY_PLACEHOLDER must contain a domain-specific example (not generic).

        S8-F8.1: Placeholder text should guide users with a relevant example.
        """
        from gui.config.text import RUN_APP_QUERY_PLACEHOLDER

        # Must be an example query (starts with "e.g." or "e.g,")
        assert RUN_APP_QUERY_PLACEHOLDER.lower().startswith("e.g"), (
            f"RUN_APP_QUERY_PLACEHOLDER must start with 'e.g.' to signal it's an example. "
            f"Got: {RUN_APP_QUERY_PLACEHOLDER!r}"
        )
        # Must reference a domain concept (paper, research, methodology, etc.)
        domain_keywords = ["paper", "research", "methodology", "query", "evaluate"]
        assert any(kw in RUN_APP_QUERY_PLACEHOLDER.lower() for kw in domain_keywords), (
            f"RUN_APP_QUERY_PLACEHOLDER must contain a domain-specific term. "
            f"Got: {RUN_APP_QUERY_PLACEHOLDER!r}"
        )


# ---------------------------------------------------------------------------
# 7. prompts.py — display-only warning must be present
# ---------------------------------------------------------------------------


class TestPromptsDisplayOnlyWarning:
    """Verify prompts.py shows a warning that edits are display-only and not saved.

    S8-F8.1: Users must be clearly informed that changes are not persisted.
    """

    def test_prompts_calls_warning_with_display_only_message(self) -> None:
        """render_prompts must call st.warning with a display-only notice.

        Behavioral: call render_prompts with a valid ChatConfig and verify
        warning() is called with text mentioning display-only or not-saved.
        """
        from unittest.mock import patch

        # Build a minimal valid ChatConfig with required fields
        from app.data_models.app_models import ChatConfig, ProviderConfig

        provider_cfg = ProviderConfig(
            model_name="gpt-4o-mini",
            base_url="http://localhost:8080",  # type: ignore[arg-type]
        )
        chat_config = ChatConfig(
            providers={"openai": provider_cfg},
            inference={"max_tokens": 1000},
            prompts={"manager": "You are a manager."},
        )

        from gui.pages import prompts as prompts_mod

        with (
            patch.object(prompts_mod, "header"),
            patch.object(prompts_mod, "warning") as mock_warning,
            patch.object(prompts_mod, "error"),
            patch.object(prompts_mod, "info"),
            patch("gui.pages.prompts.render_prompt_editor", return_value=None),
        ):
            prompts_mod.render_prompts(chat_config)

        assert mock_warning.called, (
            "render_prompts must call st.warning() to show a prominent notice."
        )
        warning_text = " ".join(
            str(call.args[0]) for call in mock_warning.call_args_list if call.args
        )
        assert "display-only" in warning_text or "not be saved" in warning_text, (
            f"warning() must mention 'display-only' or 'not be saved'. Got: {warning_text!r}"
        )
