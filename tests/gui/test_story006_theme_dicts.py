"""Tests for STORY-006: Theme dicts defined in styling.py."""

from gui.config.styling import THEMES, add_custom_styling
from unittest.mock import patch


REQUIRED_KEYS = {"primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor", "accentColor"}

EXPECTED_THEMES = {
    "expanse_dark": {
        "primaryColor": "#4A90E2",
        "backgroundColor": "#0b0c10",
        "secondaryBackgroundColor": "#1f2833",
        "textColor": "#66fcf1",
        "accentColor": "#50C878",
    },
    "nord_light": {
        "primaryColor": "#5E81AC",
        "backgroundColor": "#ECEFF4",
        "secondaryBackgroundColor": "#E5E9F0",
        "textColor": "#2E3440",
        "accentColor": "#88C0D0",
    },
    "tokyo_night": {
        "primaryColor": "#7AA2F7",
        "backgroundColor": "#1A1B26",
        "secondaryBackgroundColor": "#24283B",
        "textColor": "#C0CAF5",
        "accentColor": "#9ECE6A",
    },
}


class TestThemesDictExists:
    """Test that THEMES dict exists with exactly 3 theme keys."""

    def test_themes_has_three_keys(self):
        assert len(THEMES) == 3

    def test_themes_contains_expanse_dark(self):
        assert "expanse_dark" in THEMES

    def test_themes_contains_nord_light(self):
        assert "nord_light" in THEMES

    def test_themes_contains_tokyo_night(self):
        assert "tokyo_night" in THEMES


class TestThemeColorKeys:
    """Test each theme has all required color keys."""

    def test_expanse_dark_has_required_keys(self):
        assert set(THEMES["expanse_dark"].keys()) == REQUIRED_KEYS

    def test_nord_light_has_required_keys(self):
        assert set(THEMES["nord_light"].keys()) == REQUIRED_KEYS

    def test_tokyo_night_has_required_keys(self):
        assert set(THEMES["tokyo_night"].keys()) == REQUIRED_KEYS


class TestThemeColorValues:
    """Test exact color values for each theme."""

    def test_expanse_dark_values(self):
        assert THEMES["expanse_dark"] == EXPECTED_THEMES["expanse_dark"]

    def test_nord_light_values(self):
        assert THEMES["nord_light"] == EXPECTED_THEMES["nord_light"]

    def test_tokyo_night_values(self):
        assert THEMES["tokyo_night"] == EXPECTED_THEMES["tokyo_night"]


class TestAddCustomStylingNotBroken:
    """Test that existing add_custom_styling still works."""

    @patch("gui.config.styling.set_page_config")
    def test_add_custom_styling_calls_set_page_config(self, mock_set_page_config):
        add_custom_styling("Test Page")
        mock_set_page_config.assert_called_once_with(
            page_title="Test Page",
            page_icon="\U0001f916",
            layout="wide",
            initial_sidebar_state="expanded",
        )
