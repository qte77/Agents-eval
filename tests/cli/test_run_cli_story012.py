"""Tests for STORY-012: --paper-id, --judge-provider, --judge-model args in run_cli.py.

Covers:
- --paper-number renamed to --paper-id
- --judge-provider and --judge-model added
- JudgeSettings constructed and passed to main() when judge args provided
"""

from run_cli import _COMMANDS, parse_args


class TestPaperIdRename:
    """Tests for --paper-number → --paper-id rename in run_cli."""

    def test_paper_id_accepted(self):
        """Test that --paper-id is accepted."""
        args = parse_args(["--paper-id=42"])
        assert args.get("paper_id") == "42"

    def test_paper_id_in_commands_registry(self):
        """Test that --paper-id is documented in _COMMANDS."""
        assert "--paper-id" in _COMMANDS

    def test_paper_number_no_longer_accepted(self):
        """Test that --paper-number is no longer in _COMMANDS (renamed)."""
        assert "--paper-number" not in _COMMANDS

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

    def test_judge_provider_in_commands_registry(self):
        """Test that --judge-provider is documented in _COMMANDS."""
        assert "--judge-provider" in _COMMANDS

    def test_judge_model_in_commands_registry(self):
        """Test that --judge-model is documented in _COMMANDS."""
        assert "--judge-model" in _COMMANDS

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
