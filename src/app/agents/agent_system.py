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
from pydantic_ai.common_tools.duckduckgo import (
    duckduckgo_search_tool,  # type: ignore[reportUnknownVariableType]
)
from pydantic_ai.usage import UsageLimits

from app.agents.opik_instrumentation import (
    get_instrumentation_manager,
    initialize_opik_instrumentation,
)
from app.data_models.app_models import (
    AgentConfig,
    AnalysisResult,
    AppEnv,
    ChatConfig,
    EndpointConfig,
    ModelDict,
    ProviderConfig,
    ResearchResult,
    ResearchResultSimple,
    ResearchSummary,
    ResultBaseType,
    UserPromptType,
)
from app.data_models.peerread_models import ReviewGenerationResult
from app.evals.evaluation_config import EvaluationConfig
from app.llms.models import create_agent_models
from app.llms.providers import (
    get_api_key,
    get_provider_config,
    setup_llm_environment,
)
from app.tools.peerread_tools import (
    add_peerread_review_tools_to_manager,
    add_peerread_tools_to_manager,
)
from app.utils.error_messages import generic_exception, invalid_data_model_format
from app.utils.load_configs import OpikConfig
from app.utils.log import logger


def initialize_opik_instrumentation_from_config(config_path: str | None = None) -> None:
    """Initialize Opik instrumentation from evaluation config."""
    try:
        eval_config = EvaluationConfig(config_path)
        opik_config = OpikConfig.from_config(eval_config.config)
        initialize_opik_instrumentation(opik_config)
        logger.info(f"Opik instrumentation initialized: enabled={opik_config.enabled}")
    except Exception as e:
        logger.warning(f"Failed to initialize Opik instrumentation: {e}")


def get_opik_decorator(agent_name: str, agent_role: str, execution_phase: str):
    """Get Opik tracking decorator if available."""
    manager = get_instrumentation_manager()
    if manager and manager.config.enabled:
        return manager.track_agent_execution(agent_name, agent_role, execution_phase)
    return lambda func: func  # No-op decorator if Opik not available


def _add_tools_to_manager_agent(
    manager_agent: Agent[None, BaseModel],
    research_agent: Agent[None, BaseModel] | None = None,
    analysis_agent: Agent[None, BaseModel] | None = None,
    synthesis_agent: Agent[None, BaseModel] | None = None,
    result_type: type[
        ResearchResult | ResearchResultSimple | ReviewGenerationResult
    ] = ResearchResult,
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
            raise e
        except Exception as e:
            msg = generic_exception(str(e))
            logger.exception(msg)
            raise Exception(msg)

    if research_agent is not None:
        # Apply Opik tracing decorator
        opik_decorator = get_opik_decorator("researcher", "research", "information_gathering")

        @opik_decorator
        @manager_agent.tool
        # TODO remove redundant tool creation
        # ignore "delegate_research" is not accessed because of decorator
        async def delegate_research(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> ResearchResult | ResearchResultSimple | ReviewGenerationResult:
            """Delegate research task to ResearchAgent."""
            result = await research_agent.run(query, usage=ctx.usage)
            # result.output is already a result object from the agent
            if isinstance(
                result.output,
                ResearchResult | ResearchResultSimple | ReviewGenerationResult,
            ):
                return result.output
            else:
                return _validate_model_return(str(result.output), result_type)

    if analysis_agent is not None:
        # Apply Opik tracing decorator
        opik_decorator_analysis = get_opik_decorator("analyst", "analysis", "analytical_processing")

        @opik_decorator_analysis
        @manager_agent.tool
        # ignore "delegate_research" is not accessed because of decorator
        async def delegate_analysis(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> AnalysisResult:
            """Delegate analysis task to AnalysisAgent."""
            result = await analysis_agent.run(query, usage=ctx.usage)
            # result.output is already an AnalysisResult object from the agent
            if isinstance(result.output, AnalysisResult):
                return result.output
            else:
                return _validate_model_return(str(result.output), AnalysisResult)

    if synthesis_agent is not None:
        # Apply Opik tracing decorator
        opik_decorator_synthesis = get_opik_decorator(
            "synthesizer", "synthesis", "integration_synthesis"
        )

        @opik_decorator_synthesis
        @manager_agent.tool
        # ignore "delegate_research" is not accessed because of decorator
        async def delegate_synthesis(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> ResearchSummary:
            """Delegate synthesis task to AnalysisAgent."""
            result = await synthesis_agent.run(query, usage=ctx.usage)
            # result.output is already a ResearchSummary object from the agent
            if isinstance(result.output, ResearchSummary):
                return result.output
            else:
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


def _get_result_type(
    provider: str,
    enable_review_tools: bool = False,
) -> type[ResearchResult | ResearchResultSimple | ReviewGenerationResult]:
    """
    Select appropriate result model based on provider and tool configuration.

    Args:
        provider: The provider name (e.g., 'gemini', 'openai', etc.)
        enable_review_tools: Whether review tools are enabled for paper reviews

    Returns:
        ReviewGenerationResult when review tools are enabled
        ResearchResultSimple for Gemini (no additionalProperties support)
        ResearchResult for other providers (supports flexible union types)
    """
    # When review tools are enabled, always use ReviewGenerationResult
    if enable_review_tools:
        return ReviewGenerationResult

    # For research tasks, select based on provider capabilities
    # Gemini doesn't support additionalProperties in JSON schema
    if provider.lower() == "gemini":
        return ResearchResultSimple
    return ResearchResult


def _create_manager(
    prompts: dict[str, str],
    models: ModelDict,
    provider: str,
    enable_review_tools: bool = False,
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
            f"analyst({models.model_analyst.model_name})" if models.model_analyst else None,
            f"synthesiser({models.model_synthesiser.model_name})"
            if models.model_synthesiser
            else None,
        ]
        if agent
    ]
    status += f" with agents: {', '.join(active_agents)}" if active_agents else ""
    logger.info(status)

    # Select appropriate result type based on provider and tool configuration
    result_type = _get_result_type(provider, enable_review_tools)

    manager = _create_agent(
        AgentConfig.model_validate(
            {
                "model": models.model_manager,
                "output_type": result_type,
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
                    "output_type": result_type,
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

    _add_tools_to_manager_agent(manager, researcher, analyst, synthesiser, result_type)
    add_peerread_tools_to_manager(manager)

    return manager


def get_manager(
    provider: str,
    provider_config: ProviderConfig,
    api_key: str | None,
    prompts: dict[str, str],
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    enable_review_tools: bool = False,
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
    models = create_agent_models(
        model_config, include_researcher, include_analyst, include_synthesiser
    )
    manager = _create_manager(prompts, models, provider, enable_review_tools)

    # Conditionally add review tools based on flag
    def conditionally_add_review_tools(
        manager: Agent[None, BaseModel],
        enable: bool = False,
        max_content_length: int = 15000,
    ):
        """Conditionally add review persistence tools to the manager.

        Args:
            manager: The manager agent to potentially add tools to.
            enable: Flag to determine whether to add review tools.
            max_content_length: The maximum number of characters to include in the
                prompt.
        """
        if enable:
            add_peerread_review_tools_to_manager(manager, max_content_length=max_content_length)
        return manager

    max_content_length = provider_config.max_content_length or 15000

    return conditionally_add_review_tools(
        manager,
        enable=enable_review_tools,
        max_content_length=max_content_length,
    )


# Apply Opik tracing decorator to run_manager
@get_opik_decorator("manager", "orchestrator", "coordination")
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

    try:
        if pydantic_ai_stream:
            raise NotImplementedError(
                "Streaming currently only possible for Agents with output_type "
                "str not pydantic model"
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
        # FIXME  # type: ignore
        logger.info(f"Usage statistics: {result.usage()}")  # type: ignore
    except Exception as e:
        logger.error(f"Error in run_manager: {e}")
        raise


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
    is_api_key, api_key_msg = get_api_key(provider, chat_env_config)

    # Set up LLM environment with all available API keys
    api_keys = {
        "openai": chat_env_config.OPENAI_API_KEY,
        "anthropic": chat_env_config.ANTHROPIC_API_KEY,
        "gemini": chat_env_config.GEMINI_API_KEY,
        "github": chat_env_config.GITHUB_API_KEY,
        "grok": chat_env_config.GROK_API_KEY,
        "huggingface": chat_env_config.HUGGINGFACE_API_KEY,
        "openrouter": chat_env_config.OPENROUTER_API_KEY,
        "perplexity": chat_env_config.PERPLEXITY_API_KEY,
        "together": chat_env_config.TOGETHER_API_KEY,
    }
    setup_llm_environment(api_keys)

    if provider.lower() != "ollama" and not is_api_key:
        msg = f"API key for provider '{provider}' is not set."
        logger.error(msg)
        raise ValueError(msg)

    # TODO Separate Gemini request into function
    # FIXME GeminiModel not compatible with pydantic-ai OpenAIModel
    # ModelRequest not iterable
    # Input should be 'STOP', 'MAX_TOKENS' or 'SAFETY'
    # [type=literal_error, input_value='MALFORMED_FUNCTION_CALL', input_type=str]
    # For further information visit https://errors.pydantic.dev/2.11/v/literal_error
    # if provider.lower() == "gemini":
    #     if isinstance(query, str):
    #         query = ModelRequest.user_text_prompt(query)
    #     elif isinstance(query, list):  # type: ignore[reportUnnecessaryIsInstance]
    #         # query = [
    #         #    ModelRequest.user_text_prompt(
    #         #        str(msg.get("content", ""))
    #         #    )  # type: ignore[reportUnknownArgumentType]
    #         #    if isinstance(msg, dict)
    #         #    else msg
    #         #    for msg in query
    #         # ]
    #         raise NotImplementedError("Currently conflicting with UserPromptType")
    #     else:
    #         msg = f"Unsupported query type for Gemini: {type(query)}"
    #         logger.error(msg)
    #         raise TypeError(msg)

    # Load usage limits from config instead of hardcoding
    usage_limits = None
    if provider_config.usage_limits is not None:
        usage_limits = UsageLimits(
            request_limit=10, total_tokens_limit=provider_config.usage_limits
        )

    return EndpointConfig.model_validate(
        {
            "provider": provider,
            "query": query,
            "api_key": api_key_msg,
            "prompts": prompts,
            "provider_config": provider_config,
            "usage_limits": usage_limits,
        }
    )
