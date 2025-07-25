"""
Agent system utilities for orchestrating multi-agent workflows.

This module provides functions and helpers to create, configure, and run agent
systems using Pydantic AI. It supports delegation of tasks to research, analysis, and
synthesis agents, and manages agent configuration, environment setup, and execution.
Args:
    provider (str): The name of the provider. provider_config (ProviderConfig):
        Configuration settings for the provider.
    api_key (str): API key for authentication with the provider.
    prompts (dict[str, str]): Configuration for prompts.
    include_researcher (bool): Flag to include the researcher agent.
    include_analyst (bool): Flag to include the analyst agent.
    include_synthesiser (bool): Flag to include the synthesiser agent.
    query (str | list[dict[str, str]]): The query or messages for the agent.
    chat_config (ChatConfig): The configuration object for agents and providers.
    usage_limits (UsageLimits): Usage limits for agent execution.
    pydantic_ai_stream (bool): Whether to use Pydantic AI streaming.

Functions:
    get_manager: Initializes and returns a manager agent with the specified
        configuration.
    run_manager: Asynchronously runs the manager agent with the given query and
        provider.
    setup_agent_env: Sets up the environment for an agent by configuring provider
        settings, prompts, API key, and usage limits.
"""

from pydantic import BaseModel, ValidationError
from pydantic_ai import Agent, RunContext
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.messages import ModelRequest
from pydantic_ai.usage import UsageLimits

from src.app.agents.llm_model_funs import get_api_key, get_models, get_provider_config
from src.app.datamodels.app_models import (
    AgentConfig,
    AnalysisResult,
    AppEnv,
    ChatConfig,
    EndpointConfig,
    ModelDict,
    ProviderConfig,
    ResearchResult,
    ResearchSummary,
    ResultBaseType,
    UserPromptType,
)
from src.app.utils.error_messages import generic_exception, invalid_data_model_format
from src.app.utils.log import logger


def _add_tools_to_manager_agent(
    manager_agent: Agent[None, BaseModel],
    research_agent: Agent[None, BaseModel] | None = None,
    analysis_agent: Agent[None, BaseModel] | None = None,
    synthesis_agent: Agent[None, BaseModel] | None = None,
):
    """
    Adds tools to the manager agent for delegating tasks to research, analysis, and
        synthesis agents.
    Args:
        manager_agent (Agent): The manager agent to which tools will be added.
        research_agent (Agent): The agent responsible for handling research tasks.
        analysis_agent (Agent, optional): The agent responsible for handling
            analysis tasks. Defaults to None.
        synthesis_agent (Agent, optional): The agent responsible for handling
            synthesis tasks. Defaults to None.
    Returns:
        None
    """

    def _validate_model_return(
        result_output: str,
        result_model: type[ResultBaseType],
    ) -> ResultBaseType:
        """Validates the output against the expected model."""
        try:
            return result_model.model_validate(result_output)
        except ValidationError as e:
            msg = invalid_data_model_format(str(e))
            logger.error(msg)
            raise ValidationError(msg)
        except Exception as e:
            msg = generic_exception(str(e))
            logger.exception(msg)
            raise Exception(msg)

    if research_agent is not None:

        @manager_agent.tool
        # TODO remove redundant tool creation
        # ignore "delegate_research" is not accessed because of decorator
        async def delegate_research(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> ResearchResult:
            """Delegate research task to ResearchAgent."""
            result = await research_agent.run(query, usage=ctx.usage)
            return _validate_model_return(str(result.output), ResearchResult)

    if analysis_agent is not None:

        @manager_agent.tool
        # ignore "delegate_research" is not accessed because of decorator
        async def delegate_analysis(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> AnalysisResult:
            """Delegate analysis task to AnalysisAgent."""
            result = await analysis_agent.run(query, usage=ctx.usage)
            return _validate_model_return(str(result.output), AnalysisResult)

    if synthesis_agent is not None:

        @manager_agent.tool
        # ignore "delegate_research" is not accessed because of decorator
        async def delegate_synthesis(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> ResearchSummary:
            """Delegate synthesis task to AnalysisAgent."""
            result = await synthesis_agent.run(query, usage=ctx.usage)
            return _validate_model_return(str(result.output), ResearchSummary)


def _create_agent(agent_config: AgentConfig) -> Agent[None, BaseModel]:
    """Factory for creating configured agents"""

    return Agent(
        model=agent_config.model,
        output_type=agent_config.output_type,
        system_prompt=agent_config.system_prompt,
        tools=agent_config.tools,
        retries=agent_config.retries,
    )


def _create_manager(
    prompts: dict[str, str],
    models: ModelDict,
) -> Agent[None, BaseModel]:
    """
    Creates and configures a manager Agent with associated researcher, analyst,
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
        Agent: Configured manager agent with associated tools and agents.
    """

    status = f"Creating manager({models.model_manager.model_name})"
    active_agents = [
        agent
        for agent in [
            f"researcher({models.model_researcher.model_name})"
            if models.model_researcher
            else None,
            f"analyst({models.model_analyst.model_name})"
            if models.model_analyst
            else None,
            f"synthesiser({models.model_synthesiser.model_name})"
            if models.model_synthesiser
            else None,
        ]
        if agent
    ]
    status += f" with agents: {', '.join(active_agents)}" if active_agents else ""
    logger.info(status)

    manager = _create_agent(
        AgentConfig.model_validate(
            {
                "model": models.model_manager,
                "output_type": ResearchResult,
                "system_prompt": prompts["system_prompt_manager"],
            }
        )
    )

    if models.model_researcher is None:
        researcher = None
    else:
        researcher = _create_agent(
            AgentConfig.model_validate(
                {
                    "model": models.model_researcher,
                    "output_type": ResearchResult,
                    "system_prompt": prompts["system_prompt_researcher"],
                    "tools": [duckduckgo_search_tool()],
                }
            )
        )

    if models.model_analyst is None:
        analyst = None
    else:
        analyst = _create_agent(
            AgentConfig.model_validate(
                {
                    "model": models.model_analyst,
                    "output_type": AnalysisResult,
                    "system_prompt": prompts["system_prompt_analyst"],
                }
            )
        )

    if models.model_synthesiser is None:
        synthesiser = None
    else:
        synthesiser = _create_agent(
            AgentConfig.model_validate(
                {
                    "model": models.model_synthesiser,
                    "output_type": AnalysisResult,
                    "system_prompt": prompts["system_prompt_synthesiser"],
                }
            )
        )

    _add_tools_to_manager_agent(manager, researcher, analyst, synthesiser)
    return manager


def get_manager(
    provider: str,
    provider_config: ProviderConfig,
    api_key: str | None,
    prompts: dict[str, str],
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
) -> Agent[None, BaseModel]:
    """
    Initializes and returns a Agent manager with the specified configuration.
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
        Agent: The initialized Agent manager.
    """

    # FIXME context manager try-catch
    # with error_handling_context("get_manager()"):
    model_config = EndpointConfig.model_validate(
        {
            "provider": provider,
            "prompts": prompts,
            "api_key": api_key,
            "provider_config": provider_config,
        }
    )
    models = get_models(
        model_config, include_researcher, include_analyst, include_synthesiser
    )
    return _create_manager(prompts, models)


async def run_manager(
    manager: Agent[None, BaseModel],
    query: UserPromptType,
    provider: str,
    usage_limits: UsageLimits | None,
    pydantic_ai_stream: bool = False,
) -> None:
    """
    Asynchronously runs the manager with the given query and provider, handling errors
        and printing results.
    Args:
        manager (Agent): The system agent responsible for running the query.
        query (str): The query to be processed by the manager.
        provider (str): The provider to be used for the query.
        usage_limits (UsageLimits): The usage limits to be applied during the query
            execution.
        pydantic_ai_stream (bool, optional): Flag to enable or disable Pydantic AI
            stream. Defaults to False.
    Returns:
        None
    """

    # FIXME context manager try-catch
    # with out ? error_handling_context("run_manager()"):
    model_name = getattr(manager, "model")._model_name
    mgr_cfg = {"user_prompt": query, "usage_limits": usage_limits}
    logger.info(f"Researching with {provider}({model_name}) and Topic: {query} ...")

    if pydantic_ai_stream:
        raise NotImplementedError(
            "Streaming currently only possible for Agents with "
            "output_type str not pydantic model"
        )
        # logger.info("Streaming model response ...")
        # result = await manager.run(**mgr_cfg)
        # aync for chunk in result.stream_text():  # .run(**mgr_cfg) as result:
        # async with manager.run_stream(user_prompt=query) as stream:
        #    async for chunk in stream.stream_text():
        #        logger.info(str(chunk))
        # result = await stream.get_result()
    else:
        logger.info("Waiting for model response ...")
        # FIXME deprecated warning manager.run(), query unknown type
        # FIXME [call-overload] error: No overload variant of "run" of "Agent"
        # matches argument type "dict[str, list[dict[str, str]] |
        # Sequence[str | ImageUrl | AudioUrl | DocumentUrl | VideoUrl |
        # BinaryContent] | UsageLimits | None]"
        result = await manager.run(**mgr_cfg)  # type: ignore[reportDeprecated,reportUnknownArgumentType,reportCallOverload,call-overload]

    logger.info(f"Result: {result}")
    logger.info(f"Usage statistics: {result.usage()}")


def setup_agent_env(
    provider: str,
    query: UserPromptType,
    chat_config: ChatConfig | BaseModel,
    chat_env_config: AppEnv,
) -> EndpointConfig:
    """
    Sets up the environment for an agent by configuring provider settings, prompts,
    API key, and usage limits.

    Args:
        provider (str): The name of the provider.
        query (UserPromptType): The messages or queries to be sent to the agent.
        chat_config (ChatConfig | BaseModel): The configuration object containing
            provider and prompt settings.
        chat_env_config (AppEnv): The application environment configuration
            containing API keys.

    Returns:
        EndpointConfig: The configuration object for the agent.
    """

    if not isinstance(chat_config, ChatConfig):
        raise TypeError("'chat_config' of invalid type: ChatConfig expected")
    msg: str | None
    # FIXME context manager try-catch
    # with error_handling_context("setup_agent_env()"):
    provider_config = get_provider_config(provider, chat_config.providers)

    prompts = chat_config.prompts
    api_key = get_api_key(provider, chat_env_config)

    if provider.lower() == "ollama":
        # TODO move usage limits to config
        usage_limits = UsageLimits(request_limit=10, total_tokens_limit=100000)
    else:
        if api_key is None:
            msg = f"API key for provider '{provider}' is not set."
            logger.error(msg)
            raise ValueError(msg)
        # TODO Separate Gemini request into function
        if provider.lower() == "gemini":
            if isinstance(query, str):
                query = ModelRequest.user_text_prompt(query)
            elif isinstance(query, list):  # type: ignore[reportUnnecessaryIsInstance]
                # query = [
                #    ModelRequest.user_text_prompt(
                #        str(msg.get("content", ""))
                #    )  # type: ignore[reportUnknownArgumentType]
                #    if isinstance(msg, dict)
                #    else msg
                #    for msg in query
                # ]
                raise NotImplementedError("Currently conflicting with UserPromptType")
            else:
                msg = f"Unsupported query type for Gemini: {type(query)}"
                logger.error(msg)
                raise TypeError(msg)
        # TODO move usage limits to config
        usage_limits = UsageLimits(request_limit=10, total_tokens_limit=10000)

    return EndpointConfig.model_validate(
        {
            "provider": provider,
            "query": query,
            "api_key": api_key,
            "prompts": prompts,
            "provider_config": provider_config,
            "usage_limits": usage_limits,
        }
    )
