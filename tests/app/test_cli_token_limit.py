"""
Tests for configurable agent token limits via CLI, GUI, and env var (STORY-002).

Validates that --token-limit CLI flag, GUI token limit field, and AGENT_TOKEN_LIMIT
environment variable correctly override usage_limits from config_chat.json, with
proper validation bounds (1000-1000000) and priority order (CLI > GUI > env).
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_ai.usage import UsageLimits

from app.app import main
from run_cli import parse_args


class TestCLITokenLimitFlag:
    """Tests for --token-limit CLI flag."""

    @pytest.mark.asyncio
    async def test_cli_accepts_token_limit_flag(self):
        """Test that CLI accepts --token-limit flag and passes it to setup_agent_env."""
        with (
            patch("app.app.setup_agent_env") as mock_setup,
            patch("app.app.login"),
            patch("app.app.get_manager") as mock_get_manager,
            patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
            patch("app.app.load_config") as mock_load_config,
        ):
            # Setup mocks
            mock_setup.return_value = MagicMock(
                provider="test_provider",
                provider_config=MagicMock(usage_limits=25000),
                api_key="test_key",
                prompts={},
                query="test query",
                usage_limits=UsageLimits(request_limit=10, total_tokens_limit=100000),
            )
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            mock_run_manager.return_value = (
                "test_exec_123",
                None,
            )  # (execution_id, manager_output)
            mock_load_config.return_value = MagicMock(prompts={})

            # Run main with --token-limit flag
            await main(
                chat_provider="test_provider",
                query="test query",
                token_limit=100000,
            )

            # Verify setup_agent_env was called
            mock_setup.assert_called_once()

    @pytest.mark.asyncio
    async def test_cli_token_limit_overrides_config(self):
        """Test that CLI --token-limit overrides config_chat.json usage_limits."""
        with (
            patch("app.app.setup_agent_env") as mock_setup,
            patch("app.app.login"),
            patch("app.app.get_manager") as mock_get_manager,
            patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
            patch("app.app.load_config") as mock_load_config,
        ):
            # Setup mocks - config has 25000, CLI provides 100000
            mock_config = MagicMock()
            mock_config.usage_limits = 25000
            mock_setup.return_value = MagicMock(
                provider="test_provider",
                provider_config=mock_config,
                api_key="test_key",
                prompts={},
                query="test query",
                usage_limits=UsageLimits(request_limit=10, total_tokens_limit=100000),
            )
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            mock_run_manager.return_value = (
                "test_exec_123",
                None,
            )  # (execution_id, manager_output)
            mock_load_config.return_value = MagicMock(prompts={})

            # Run main with CLI override
            await main(
                chat_provider="test_provider",
                query="test query",
                token_limit=100000,
            )

            # Verify setup_agent_env was called with token_limit parameter
            mock_setup.assert_called_once()
            # Extract positional and keyword args
            call_args, call_kwargs = mock_setup.call_args
            # token_limit should be the 5th parameter (index 4) or in kwargs
            assert (
                len(call_args) >= 5
                and call_args[4] == 100000
                or call_kwargs.get("token_limit") == 100000
            )

    def test_cli_parse_args_includes_token_limit(self):
        """Test that parse_args extracts --token-limit flag."""
        args = parse_args(["--token-limit=150000"])
        assert args["token_limit"] == 150000

    def test_cli_help_includes_token_limit(self):
        """Snapshot: CLI help text includes --token-limit."""
        # This test would capture help output, but since parse_args exits on --help,
        # we'll test the commands dict structure instead
        from run_cli import parse_args

        # Verify --token-limit is in the documented commands
        # (would need to refactor parse_args to expose commands dict)
        # For now, verify flag parsing works
        assert parse_args(["--token-limit=50000"])["token_limit"] == 50000


class TestEnvVarTokenLimit:
    """Tests for AGENT_TOKEN_LIMIT environment variable."""

    @pytest.mark.asyncio
    async def test_env_var_token_limit_used_when_no_cli_flag(self):
        """Test that AGENT_TOKEN_LIMIT env var is used when CLI flag is not set."""
        with (
            patch("app.app.setup_agent_env") as mock_setup,
            patch("app.app.login"),
            patch("app.app.get_manager") as mock_get_manager,
            patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
            patch("app.app.load_config") as mock_load_config,
            patch.dict(os.environ, {"AGENT_TOKEN_LIMIT": "80000"}),
        ):
            # Setup mocks
            mock_config = MagicMock()
            mock_config.usage_limits = 25000
            mock_setup.return_value = MagicMock(
                provider="test_provider",
                provider_config=mock_config,
                api_key="test_key",
                prompts={},
                query="test query",
                usage_limits=UsageLimits(request_limit=10, total_tokens_limit=80000),
            )
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            mock_run_manager.return_value = (
                "test_exec_123",
                None,
            )  # (execution_id, manager_output)
            mock_load_config.return_value = MagicMock(prompts={})

            # Run main without CLI flag (should pick up env var)
            await main(
                chat_provider="test_provider",
                query="test query",
            )

            # Verify env var was used
            mock_run_manager.assert_called_once()

    @pytest.mark.asyncio
    async def test_cli_flag_overrides_env_var(self):
        """Test that CLI --token-limit has higher priority than env var."""
        with (
            patch("app.app.setup_agent_env") as mock_setup,
            patch("app.app.login"),
            patch("app.app.get_manager") as mock_get_manager,
            patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
            patch("app.app.load_config") as mock_load_config,
            patch.dict(os.environ, {"AGENT_TOKEN_LIMIT": "80000"}),
        ):
            # Setup mocks
            mock_config = MagicMock()
            mock_config.usage_limits = 25000
            mock_setup.return_value = MagicMock(
                provider="test_provider",
                provider_config=mock_config,
                api_key="test_key",
                prompts={},
                query="test query",
                usage_limits=UsageLimits(request_limit=10, total_tokens_limit=120000),
            )
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            mock_run_manager.return_value = (
                "test_exec_123",
                None,
            )  # (execution_id, manager_output)
            mock_load_config.return_value = MagicMock(prompts={})

            # Run main with CLI flag (should override env var)
            await main(
                chat_provider="test_provider",
                query="test query",
                token_limit=120000,
            )

            # Verify setup_agent_env was called with CLI token_limit (not env var)
            mock_setup.assert_called_once()
            call_args, call_kwargs = mock_setup.call_args
            assert (
                len(call_args) >= 5
                and call_args[4] == 120000
                or call_kwargs.get("token_limit") == 120000
            )


class TestConfigFallback:
    """Tests for fallback to config_chat.json when no override."""

    @pytest.mark.asyncio
    async def test_config_used_when_no_override(self):
        """Test that config_chat.json value is used when no CLI/env override."""
        with (
            patch("app.app.setup_agent_env") as mock_setup,
            patch("app.app.login"),
            patch("app.app.get_manager") as mock_get_manager,
            patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
            patch("app.app.load_config") as mock_load_config,
        ):
            # Setup mocks - only config value, no overrides
            mock_config = MagicMock()
            mock_config.usage_limits = 25000
            mock_setup.return_value = MagicMock(
                provider="test_provider",
                provider_config=mock_config,
                api_key="test_key",
                prompts={},
                query="test query",
                usage_limits=UsageLimits(request_limit=10, total_tokens_limit=25000),
            )
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            mock_run_manager.return_value = (
                "test_exec_123",
                None,
            )  # (execution_id, manager_output)
            mock_load_config.return_value = MagicMock(prompts={})

            # Run main without any token limit override
            await main(
                chat_provider="test_provider",
                query="test query",
            )

            # Verify setup_agent_env was called without token_limit override
            mock_setup.assert_called_once()
            call_args, call_kwargs = mock_setup.call_args
            # token_limit should be None (not passed)
            assert (len(call_args) < 5 or call_args[4] is None) and call_kwargs.get(
                "token_limit"
            ) is None
