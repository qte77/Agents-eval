"""
Agent factory functions for creating PydanticAI agents.

This module provides factory functions for creating different types of agents
with appropriate models, tools, and configurations. It separates agent creation
logic from model creation and orchestration.
"""

from pydantic_ai import Agent
from pydantic_ai.models import Model

from app.data_models.app_models import EndpointConfig, ModelDict
from app.llms.models import create_agent_models, create_simple_model
from app.utils.log import logger


class AgentFactory:
    """Factory class for creating different types of agents."""

    def __init__(self, endpoint_config: EndpointConfig | None = None):
        """Initialize agent factory with model configuration."""
        self.endpoint_config = endpoint_config
        self._models: ModelDict | None = None

    def get_models(
        self,
        include_researcher: bool = False,
        include_analyst: bool = False,
        include_synthesiser: bool = False,
    ) -> ModelDict:
        """Get or create models for agents."""
        if self._models is None and self.endpoint_config:
            self._models = create_agent_models(
                self.endpoint_config,
                include_researcher=include_researcher,
                include_analyst=include_analyst,
                include_synthesiser=include_synthesiser,
            )
        return self._models or ModelDict.model_validate(
            {
                "model_manager": None,
                "model_researcher": None,
                "model_analyst": None,
                "model_synthesiser": None,
            }
        )

    def create_manager_agent(self, system_prompt: str | None = None) -> Agent:
        """Create a manager agent with delegation capabilities."""
        models = self.get_models()
        if not models.model_manager:
            raise ValueError("Manager model not available")

        agent = Agent(
            model=models.model_manager,
            system_prompt=system_prompt
            or "You are a manager agent responsible for coordinating tasks.",
        )

        logger.info("Created manager agent")
        return agent

    def create_researcher_agent(self, system_prompt: str | None = None) -> Agent:
        """Create a researcher agent for information gathering."""
        models = self.get_models(include_researcher=True)
        if not models.model_researcher:
            raise ValueError("Researcher model not available")

        agent = Agent(
            model=models.model_researcher,
            system_prompt=system_prompt
            or "You are a researcher agent specialized in information gathering.",
        )

        logger.info("Created researcher agent")
        return agent

    def create_analyst_agent(self, system_prompt: str | None = None) -> Agent:
        """Create an analyst agent for data analysis."""
        models = self.get_models(include_analyst=True)
        if not models.model_analyst:
            raise ValueError("Analyst model not available")

        agent = Agent(
            model=models.model_analyst,
            system_prompt=system_prompt
            or "You are an analyst agent specialized in data analysis.",
        )

        logger.info("Created analyst agent")
        return agent

    def create_synthesiser_agent(self, system_prompt: str | None = None) -> Agent:
        """Create a synthesiser agent for combining results."""
        models = self.get_models(include_synthesiser=True)
        if not models.model_synthesiser:
            raise ValueError("Synthesiser model not available")

        agent = Agent(
            model=models.model_synthesiser,
            system_prompt=system_prompt
            or "You are a synthesiser agent specialized in combining information.",
        )

        logger.info("Created synthesiser agent")
        return agent


def create_evaluation_agent(
    provider: str,
    model_name: str,
    assessment_type: str,
    api_key: str | None = None,
    system_prompt: str | None = None,
    prompts: dict[str, str] | None = None,
) -> Agent:
    """
    Create an agent specifically for evaluation tasks.

    Args:
        provider: LLM provider (e.g., "openai", "github")
        model_name: Model name (e.g., "gpt-4o-mini")
        assessment_type: Type of assessment (e.g., "technical_accuracy")
        api_key: API key (optional)
        system_prompt: Custom system prompt (optional)
        prompts: Prompt configuration dictionary (optional)

    Returns:
        Agent configured for evaluation tasks
    """
    model = create_simple_model(provider, model_name, api_key)

    # Try to get system prompt from prompts config first
    if system_prompt is None and prompts:
        prompt_keys = {
            "technical_accuracy": f"system_prompt_evaluator_{assessment_type}",
            "constructiveness": f"system_prompt_evaluator_{assessment_type}",
            "planning_rationality": f"system_prompt_evaluator_{assessment_type}",
        }

        prompt_key = prompt_keys.get(assessment_type, "system_prompt_evaluator_general")
        system_prompt = prompts.get(prompt_key)

    # Fallback to default prompts if not found in config
    if system_prompt is None:
        default_prompts = {
            "technical_accuracy": (
                "You are an expert at evaluating technical accuracy of reviews. "
                "Focus on factual correctness and methodology understanding."
            ),
            "constructiveness": (
                "You are an expert at evaluating constructiveness of academic reviews. "
                "Focus on actionable feedback and balanced critique."
            ),
            "planning_rationality": (
                "You are an expert at evaluating planning quality of agent executions. "
                "Focus on logical flow and decision quality."
            ),
            "general": (
                "You are an expert evaluator providing structured assessments "
                "of text quality and content."
            ),
        }
        system_prompt = default_prompts.get(assessment_type, default_prompts["general"])

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
    )

    logger.info(
        f"Created evaluation agent for {assessment_type} using {provider}/{model_name}"
    )
    return agent


def create_simple_agent(model: Model, system_prompt: str) -> Agent:
    """
    Create a simple agent with provided model and prompt.

    Args:
        model: PydanticAI model instance
        system_prompt: System prompt for the agent

    Returns:
        Configured Agent instance
    """
    agent = Agent(model=model, system_prompt=system_prompt)
    logger.info("Created simple agent")
    return agent
