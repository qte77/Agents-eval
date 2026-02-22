"""Tests for --engine flag in run_cli.py (STORY-013).

Covers:
- --engine=mas is default
- --engine=cc is accepted
"""

from unittest.mock import patch

from run_cli import parse_args


class TestEngineArgParsing:
    """Tests for --engine argument parsing in run_cli.parse_args."""

    def test_engine_mas_is_accepted(self):
        """Test that --engine=mas is accepted."""
        args = parse_args(["--engine=mas"])
        assert args.get("engine") == "mas"

    def test_engine_cc_is_accepted(self):
        """Test that --engine=cc is accepted."""
        args = parse_args(["--engine=cc"])
        assert args.get("engine") == "cc"

    def test_engine_defaults_to_mas_when_not_specified(self):
        """Test that engine defaults to 'mas' when --engine flag not given."""
        args = parse_args(["--query=test"])
        assert args.get("engine") == "mas"

    def test_engine_registered_in_parser(self):
        """Test that --engine is a recognized argument in the parser."""
        from run_cli import _parser

        option_strings = {a for action in _parser._actions for a in action.option_strings}
        assert "--engine" in option_strings


class TestEngineMASUnchanged:
    """Tests that --engine=mas preserves the existing MAS execution path."""

    def test_engine_mas_does_not_require_claude_cli(self):
        """Test that --engine=mas works even if claude CLI is not on PATH."""
        with patch("shutil.which", return_value=None):
            args = parse_args(["--engine=mas", "--query=test"])
            # MAS engine should parse fine even without claude
            assert args.get("engine") == "mas"

    def test_engine_arg_does_not_conflict_with_other_flags(self):
        """Test that --engine can be combined with other existing flags."""
        args = parse_args(["--engine=mas", "--skip-eval"])
        assert args.get("engine") == "mas"
        assert args.get("skip_eval") is True
