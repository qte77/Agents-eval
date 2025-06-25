from app.agents.agent_system import get_manager
from app.config.data_models import ProviderConfig


def test_get_manager_minimal():
    provider = "github"
    provider_config = ProviderConfig.model_validate(
        {"model_name": "test-model", "base_url": "http://test.com"}
    )
    api_key = "test"
    prompts = {"system_prompt_manager": "test"}
    agent = get_manager(provider, provider_config, api_key, prompts)
    assert hasattr(agent, "run")
