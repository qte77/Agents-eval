"""Tests for STORY-012: --paper-id, --judge-provider, --judge-model args in run_cli.py.

Covers:
- --paper-number renamed to --paper-id
- --judge-provider and --judge-model added
- JudgeSettings constructed and passed to main() when judge args provided
"""

import pytest

from run_cli import _parser, parse_args


class TestPaperIdRename:
    """Tests for --paper-number → --paper-id rename in run_cli."""

    def test_paper_id_accepted(self):
        """Test that --paper-id is accepted."""
        args = parse_args(["--paper-id=42"])
        assert args.get("paper_id") == "42"

    def test_paper_id_registered_in_parser(self):
        """Test that --paper-id is a recognized argument."""
        option_strings = {a for action in _parser._actions for a in action.option_strings}
        assert "--paper-id" in option_strings

    def test_paper_number_not_registered(self):
        """Test that --paper-number is not a recognized argument (renamed)."""
        option_strings = {a for action in _parser._actions for a in action.option_strings}
        assert "--paper-number" not in option_strings

    def test_paper_number_rejected(self):
        """Test that --paper-number is rejected by argparse."""
        with pytest.raises(SystemExit):
            parse_args(["--paper-number=42"])

    def test_paper_id_as_string(self):
        """Test that paper_id is a string (supports arxiv IDs like '1105.1072')."""
        args = parse_args(["--paper-id=1105.1072"])
        assert args.get("paper_id") == "1105.1072"
        # Must be a string, not an int
        assert isinstance(args.get("paper_id"), str)


class TestJudgeProviderArgs:
    """Tests for --judge-provider and --judge-model args in run_cli."""

    def test_judge_provider_accepted(self):
        """Test that --judge-provider is accepted."""
        args = parse_args(["--judge-provider=openai"])
        assert args.get("judge_provider") == "openai"

    def test_judge_model_accepted(self):
        """Test that --judge-model is accepted."""
        args = parse_args(["--judge-model=gpt-4o"])
        assert args.get("judge_model") == "gpt-4o"

    def test_judge_provider_auto_value(self):
        """Test that --judge-provider=auto is accepted."""
        args = parse_args(["--judge-provider=auto"])
        assert args.get("judge_provider") == "auto"

    def test_all_new_args_combined(self):
        """Test combining --paper-id, --judge-provider, and --judge-model."""
        args = parse_args(
            ["--paper-id=1105.1072", "--judge-provider=openai", "--judge-model=gpt-4o"]
        )
        assert args.get("paper_id") == "1105.1072"
        assert args.get("judge_provider") == "openai"
        assert args.get("judge_model") == "gpt-4o"


class TestSpaceSeparatedArgs:
    """Tests for space-separated argument parsing (--flag value)."""

    def test_paper_id_space_separated(self):
        """--paper-id 1105.1072 should parse as string value, not boolean."""
        args = parse_args(["--paper-id", "1105.1072"])
        assert args.get("paper_id") == "1105.1072"

    def test_chat_provider_space_separated(self):
        """--chat-provider cerebras should parse as string value, not boolean."""
        args = parse_args(["--chat-provider", "cerebras"])
        assert args.get("chat_provider") == "cerebras"

    def test_judge_provider_space_separated(self):
        """--judge-provider openai should parse as string value."""
        args = parse_args(["--judge-provider", "openai"])
        assert args.get("judge_provider") == "openai"

    def test_mixed_equals_and_space_formats(self):
        """Mixing --key=value and --key value in same invocation."""
        args = parse_args(
            [
                "--paper-id",
                "1105.1072",
                "--chat-provider=cerebras",
                "--judge-model",
                "gpt-4o",
            ]
        )
        assert args.get("paper_id") == "1105.1072"
        assert args.get("chat_provider") == "cerebras"
        assert args.get("judge_model") == "gpt-4o"

    def test_boolean_flag_stays_boolean(self):
        """Boolean flags like --include-researcher should remain True, not consume next arg."""
        args = parse_args(["--include-researcher", "--paper-id", "42"])
        assert args.get("include_researcher") is True
        assert args.get("paper_id") == "42"
