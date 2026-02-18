"""
Tests for STORY-012: Standalone a11y/usability fixes for the GUI.

Covers:
- styling.py: CSS radio button circle hiding hack removed
- log_capture.py: text-prefix badges ([WARN], [ERR], etc.) added
- log_capture.py: module text color #999999 -> #696969 (contrast fix)
- run_gui.py: include_researcher and include_analyst default to True
- sidebar.py: radio label is "Navigation" not " "

Mock strategy:
- No real Streamlit runtime needed
- Source code inspection for CSS/text checks
- Direct function calls with patched streamlit for behavioral checks
"""

import importlib
import inspect


# ---------------------------------------------------------------------------
# 1. styling.py — CSS radio button circle hiding hack must be removed
# ---------------------------------------------------------------------------


class TestStylingRadioHackRemoved:
    """Verify the radio circle hiding CSS hack is not in styling.py.

    WCAG 1.3.3, 1.4.1: Native selection indicators must not be hidden via CSS.
    """

    def test_radio_circle_css_hack_not_in_styling_source(self) -> None:
        """styling.py must not contain the CSS that hides radio button circles.

        The hack was: div[role="radiogroup"] label > div:first-child { display: none !important; }
        or equivalent patterns hiding .stRadio first-child elements.
        """
        import gui.config.styling as styling_mod

        source = inspect.getsource(styling_mod)
        # Check neither 'display: none' targeting radio elements nor the specific selector
        assert "display: none" not in source, (
            "styling.py must not hide native radio button circles via 'display: none'"
        )

    def test_radio_circle_css_hack_not_contain_radiogroup_hide(self) -> None:
        """styling.py must not contain radiogroup-targeting CSS that hides elements."""
        import gui.config.styling as styling_mod

        source = inspect.getsource(styling_mod)
        assert "radiogroup" not in source.lower() or "display: none" not in source, (
            "Radio group elements must not be hidden via CSS"
        )


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
        assert "[INFO]" in html, (
            f"HTML must include text badge for INFO level, got: {html[:300]}"
        )

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

    def test_log_capture_source_does_not_use_low_contrast_color(self) -> None:
        """log_capture.py must not use #999999 for text color."""
        import gui.utils.log_capture as log_capture_mod

        source = inspect.getsource(log_capture_mod)
        assert "#999999" not in source, (
            "log_capture.py must not use #999999 (contrast 2.8:1 fails WCAG 1.4.3). "
            "Use #696969 (contrast 5.9:1) instead."
        )

    def test_log_capture_source_uses_accessible_color(self) -> None:
        """log_capture.py must use #696969 for module text color (WCAG 1.4.3)."""
        import gui.utils.log_capture as log_capture_mod

        source = inspect.getsource(log_capture_mod)
        assert "#696969" in source, (
            "log_capture.py must use #696969 for module text color (contrast 5.9:1, WCAG AA)."
        )


# ---------------------------------------------------------------------------
# 4. run_gui.py — default sub-agents must be True
# ---------------------------------------------------------------------------


class TestRunGuiSubAgentDefaults:
    """Verify get_session_state_defaults returns True for researcher and analyst.

    S8-F8.1: default sub-agents to True for better UX.
    """

    def test_get_session_state_defaults_include_researcher_is_true(self) -> None:
        """get_session_state_defaults must return include_researcher=True."""
        # Reload module to get fresh defaults (avoids cached module state)
        import run_gui

        importlib.reload(run_gui)
        defaults = run_gui.get_session_state_defaults()
        assert defaults["include_researcher"] is True, (
            f"Expected include_researcher=True, got {defaults['include_researcher']}"
        )

    def test_get_session_state_defaults_include_analyst_is_true(self) -> None:
        """get_session_state_defaults must return include_analyst=True."""
        import run_gui

        importlib.reload(run_gui)
        defaults = run_gui.get_session_state_defaults()
        assert defaults["include_analyst"] is True, (
            f"Expected include_analyst=True, got {defaults['include_analyst']}"
        )

    def test_get_session_state_defaults_include_synthesiser_stays_false(self) -> None:
        """get_session_state_defaults must keep include_synthesiser=False (not changed by AC)."""
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

    def test_sidebar_source_uses_navigation_label(self) -> None:
        """sidebar.py radio must use 'Navigation' as the label text."""
        import gui.components.sidebar as sidebar_mod

        source = inspect.getsource(sidebar_mod)
        assert '"Navigation"' in source or "'Navigation'" in source, (
            "sidebar.py must use 'Navigation' as the radio label, not ' ' (space)."
        )

    def test_sidebar_source_does_not_use_space_label(self) -> None:
        """sidebar.py radio must not use ' ' (space-only) as the label."""
        import gui.components.sidebar as sidebar_mod

        source = inspect.getsource(sidebar_mod)
        # The old pattern was: sidebar.radio(" ", PAGES)
        assert 'radio(" "' not in source and "radio(' '" not in source, (
            "sidebar.py must not use ' ' (space) as radio label — use 'Navigation' instead."
        )

    def test_sidebar_source_uses_label_visibility_collapsed(self) -> None:
        """sidebar.py must use label_visibility='collapsed' to hide label visually."""
        import gui.components.sidebar as sidebar_mod

        source = inspect.getsource(sidebar_mod)
        assert "label_visibility" in source and "collapsed" in source, (
            "sidebar.py must use label_visibility='collapsed' on the Navigation radio."
        )

    def test_sidebar_phoenix_link_warns_opens_in_new_tab(self) -> None:
        """sidebar.py Phoenix link must include '(opens in new tab)' text.

        S8-F8.1: Warn users that the link opens in a new tab (WCAG 3.2.5).
        """
        import gui.components.sidebar as sidebar_mod

        source = inspect.getsource(sidebar_mod)
        assert "opens in new tab" in source, (
            "sidebar.py Phoenix link must include '(opens in new tab)' text for WCAG 3.2.5."
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

    def test_prompts_source_contains_display_only_warning(self) -> None:
        """prompts.py must include a warning that edits are display-only."""
        import gui.pages.prompts as prompts_mod

        source = inspect.getsource(prompts_mod)
        # Check for warning call with display-only messaging
        assert "warning(" in source, (
            "prompts.py must call warning() to display a prominent notice."
        )
        assert "display-only" in source or "not be saved" in source, (
            "prompts.py warning must state edits are display-only or will not be saved."
        )
