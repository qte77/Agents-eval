"""Shared fixtures for tests/agents/ test modules.

Provides common agent test fixtures to avoid duplication across test files.
Fixtures here are auto-discovered by pytest for all tests in this directory.
"""

import pytest

from app.data_models.app_models import EndpointConfig, ProviderConfig


@pytest.fixture
def mock_endpoint_config():
    """Create mock endpoint configuration for agent tests.

    Returns:
        EndpointConfig: Standard test configuration with OpenAI provider.
    """
    return EndpointConfig(
        provider="openai",
        api_key="test-key",
        prompts={"manager": "You are a manager"},
        provider_config=ProviderConfig(
            model_name="gpt-4",
            base_url="https://api.openai.com/v1",
        ),
    )
