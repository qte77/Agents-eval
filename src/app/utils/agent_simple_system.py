"""
This module defines the SystemAgent class and related functions for creating and
managing agents that can research, analyze, and synthesize data using various models
and tools.

Classes:
    SystemAgent: A generic system agent for research and analysis tasks.

Functions:
    _add_tools_to_manager_agent: Adds tools to the manager agent for delegating tasks to
        other agents.
    _create_manager: Creates and configures a manager SystemAgent with associated
        researcher, analyst, and synthesiser agents.
    get_manager: Initializes and returns a SystemAgent manager with the specified
        configuration.
    run_manager: Asynchronously runs the manager with the given query and provider,
        handling errors and printing results.
"""

from pydantic_ai import Agent, RunContext
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.usage import UsageLimits

from .data_models import (
    AgentConfig,
    AnalysisResult,
    ChatConfig,
    ModelConfig,
    ProviderConfig,
    ResearchResult,
    ResearchSummary,
)
from .llm_models import get_api_key, get_models, get_provider_config
from .log import logger
from .utils import error_handling_context


class SystemAgent(Agent):
    """A generic system agent that can be used to research and analyze data."""

    def __init__(
        self,
        model: OpenAIModel,
        result_type: str | ResearchResult | AnalysisResult | ResearchSummary,
        system_prompt: str,
        result_retries: int = 3,
        tools: list = [],
    ):
        super().__init__(
            model=model,
            result_type=result_type,
            system_prompt=system_prompt,
            result_retries=result_retries,
            tools=tools,
        )


def _add_tools_to_manager_agent(
    manager_agent: SystemAgent,
    research_agent: SystemAgent | None = None,
    analysis_agent: SystemAgent | None = None,
    synthesis_agent: SystemAgent | None = None,
) -> None:
    """
    Adds tools to the manager agent for delegating tasks to research, analysis, and
        synthesis agents.
    Args:
        manager_agent (SystemAgent): The manager agent to which tools will be added.
        research_agent (SystemAgent): The agent responsible for handling research tasks.
        analysis_agent (SystemAgent, optional): The agent responsible for handling
            analysis tasks. Defaults to None.
        synthesis_agent (SystemAgent, optional): The agent responsible for handling
            synthesis tasks. Defaults to None.
    Returns:
        None
    """

    @manager_agent.tool
    async def delegate_research(ctx: RunContext[None], query: str) -> ResearchResult:
        """Delegate research task to ResearchAgent."""
        result = await research_agent.run(query, usage=ctx.usage)
        return result.data

    if analysis_agent is not None:

        @manager_agent.tool
        async def delegate_analysis(ctx: RunContext[None], data: str) -> AnalysisResult:
            """Delegate analysis task to AnalysisAgent."""
            result = await analysis_agent.run(data, usage=ctx.usage)
            return result.data

    if synthesis_agent is not None:

        @manager_agent.tool
        async def delegate_synthesis(
            ctx: RunContext[None], data: str
        ) -> ResearchSummary:
            """Delegate synthesis task to AnalysisAgent."""
            result = await synthesis_agent.run(data, usage=ctx.usage)
            return result.data


def _create_manager(
    prompts: dict[str, str],
    model_manager: GeminiModel | OpenAIModel,
    model_researcher: GeminiModel | OpenAIModel | None = None,
    model_analyst: GeminiModel | OpenAIModel | None = None,
    model_synthesiser: GeminiModel | OpenAIModel | None = None,
) -> SystemAgent:
    """
    Creates and configures a manager SystemAgent with associated researcher, analyst,
    and optionally synthesiser agents.
    Args:
        prompts (Dict[str, str]): Dictionary containing system prompts for each agent.
        model_manager (GeminiModel | OpenAIModel): Model to be used by the manager
            agent.
        model_researcher (GeminiModel | OpenAIModel | None, optional): Model to be used
            by the researcher agent.
        model_analyst (GeminiModel | OpenAIModel | None, optional): Model to be used by
            the analyst agent. Defaults to None.
        model_synthesiser (GeminiModel | OpenAIModel | None, optional): Model to be used
            by the synthesiser agent. Defaults to None.
    Returns:
        SystemAgent: Configured manager agent with associated tools and agents.
    """

    status = f"Creating manager({model_manager.model_name})"
    if model_researcher or model_analyst or model_synthesiser:
        status += " with agents: "
    manager = SystemAgent(
        model=model_manager,
        result_type=ResearchResult,
        system_prompt=prompts["system_prompt_manager"],
    )
    if model_researcher is None:
        researcher = None
    else:
        researcher = SystemAgent(
            model=model_researcher,
            result_type=ResearchResult,
            system_prompt=prompts["system_prompt_researcher"],
            tools=[duckduckgo_search_tool()],
        )
        status = f"{status}, analyist({model_researcher.model_name})"
    if model_analyst is None:
        analyst = None
    else:
        analyst = SystemAgent(
            model=model_analyst,
            result_type=AnalysisResult,
            system_prompt=prompts["system_prompt_analyst"],
        )
        status = f"{status}, analyst({model_analyst.model_name})"
    if model_synthesiser is None:
        synthesiser = None
    else:
        synthesiser = SystemAgent(
            model=model_synthesiser,
            result_type=ResearchSummary,
            system_prompt=prompts["system_prompt_synthesiser"],
        )
        status = f"{status} and synthesiser({model_synthesiser.model_name})"

    _add_tools_to_manager_agent(manager, researcher, analyst, synthesiser)
    print(status)
    return manager


def get_manager(
    provider: str,
    provider_config: ProviderConfig,
    api_key: str | None,
    prompts: dict[str, str],
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
) -> SystemAgent:
    """
    Initializes and returns a SystemAgent manager with the specified configuration.
    Args:
        provider (str): The name of the provider.
        provider_config (ProviderConfig): Configuration settings for the provider.
        api_key (str): API key for authentication with the provider.
        prompts (PromptsConfig): Configuration for prompts.
        include_researcher (bool, optional): Flag to include analyst model.
            Defaults to False.
        include_analyst (bool, optional): Flag to include analyst model.
            Defaults to False.
        include_synthesiser (bool, optional): Flag to include synthesiser model.
            Defaults to False.
    Returns:
        SystemAgent: The initialized SystemAgent manager.
    """

    # FIXME context maager try-catch
    # with error_handling_context("get_manager()"):
    model_config = ModelConfig.model_validate(  # FIXME
        {
            "provider": provider,
            "model_name": provider_config.model_name,
            "base_url": provider_config.base_url,
            "api_key": api_key,
        }
    )
    models = get_models(
        model_config, include_researcher, include_analyst, include_synthesiser
    )
    return _create_manager(
        prompts,
        **models,  # type: ignore
    )


async def run_manager(
    manager: SystemAgent,
    query: str | list[dict[str, str]],
    provider: str,
    usage_limits: UsageLimits,
    pydantic_ai_stream: bool = False,
) -> None:
    """
    Asynchronously runs the manager with the given query and provider, handling errors
        and printing results.
    Args:
        manager (SystemAgent): The system agent responsible for running the query.
        query (str): The query to be processed by the manager.
        provider (str): The provider to be used for the query.
        usage_limits (UsageLimits): The usage limits to be applied during the query
            execution.
        pydantic_ai_stream (bool, optional): Flag to enable or disable Pydantic AI
            stream. Defaults to False.
    Returns:
        None
    """

    # FIXME context maager try-catch
    # with error_handling_context("run_manager()"):
    model_name = getattr(manager, "model")._model_name
    mgr_cfg = {"user_prompt": query, "usage_limits": usage_limits}
    logger.info(
        f"\n ==> Researching with "
        f"[info][bold]{provider}({model_name})[/bold][/info] "
        f"and Topic: [debug]{query}[/debug] ...\n"
    )
    if pydantic_ai_stream:
        print("Streaming model responses...\n")
        raise NotImplementedError
        # TODO stream output: requires async functions and await
        # with manager.run_stream(**mgr_cfg) as result:
        #    for message in result.stream_text(delta=True, debounce_by=0.01):
        #        print(message, end="", flush=True)
    else:
        result = await manager.run(**mgr_cfg)

    logger.info("\n ==> Result")
    logger.info(result)
    logger.info("\n ==> Usage statistics")
    logger.info(result.usage())


def setup_agent_env(
    provider: str,
    query: str | list[dict[str, str]],
    chat_config: ChatConfig,
) -> AgentConfig:
    """
    Sets up the environment for an agent by configuring provider settings, prompts,
    API key, and usage limits.

    Args:
        provider (str): The name of the provider.
        messages (str): The messages or queries to be sent to the agent.
        config (ChatConfig): The configuration object containing provider and prompt
            settings.

    Returns:
        AgentConfig: The configuration object for the agent.
    """

    with error_handling_context("setup_agent_env()"):
        provider_config = get_provider_config(provider, chat_config.providers)

        prompts = chat_config.prompts
        api_key = get_api_key(provider)

        if provider.lower() == "ollama":
            usage_limits = UsageLimits(request_limit=10, total_tokens_limit=100000)
        else:
            if api_key is None:
                msg = f"API key for provider '{provider}' is not set."
                logger.error(msg)
                raise ValueError(msg)
            if provider.lower() == "gemini":
                if isinstance(query, str):
                    query = [{"role": "user", "content": query}]
                elif isinstance(query, list):
                    if not all(isinstance(msg, dict) for msg in query):
                        msg = "Invalid message format for Gemini provider"
                        logger.error(msg)
                        raise ValueError(msg)
                else:
                    msg = f"Unsupported query type for Gemini: {type(query)}"
                    logger.error(msg)
                    raise TypeError(msg)
            usage_limits = UsageLimits(request_limit=10, total_tokens_limit=10000)

        return AgentConfig.model_validate(
            {
                "provider": provider,
                "query": query,
                "api_key": api_key,
                "prompts": prompts,
                "provider_config": provider_config,
                "usage_limits": usage_limits,
            }
        )
