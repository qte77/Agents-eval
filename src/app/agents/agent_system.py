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

import time
import uuid
from typing import Any, NoReturn

from pydantic import BaseModel, ValidationError
from pydantic_ai import Agent, RunContext
from pydantic_ai.common_tools.duckduckgo import (
    duckduckgo_search_tool,  # type: ignore[reportUnknownVariableType]
)
from pydantic_ai.exceptions import ModelHTTPError, UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

from app.agents.logfire_instrumentation import initialize_logfire_instrumentation
from app.data_models.app_models import (
    PROVIDER_REGISTRY,
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
from app.judge.settings import JudgeSettings
from app.judge.trace_processors import get_trace_collector
from app.llms.models import create_agent_models
from app.llms.providers import (
    get_api_key,
    get_provider_config,
    setup_llm_environment,
)
from app.tools.peerread_tools import add_peerread_tools_to_agent
from app.utils.error_messages import generic_exception, invalid_data_model_format
from app.utils.load_configs import LogfireConfig
from app.utils.log import logger


def initialize_logfire_instrumentation_from_settings(
    settings: JudgeSettings | None = None,
) -> None:
    """Initialize Logfire instrumentation from JudgeSettings.

    Uses logfire.instrument_pydantic_ai() for automatic tracing.
    No manual decorators needed - all PydanticAI agents auto-instrumented.

    Args:
        settings: JudgeSettings instance. If None, uses default JudgeSettings().
    """
    try:
        if settings is None:
            settings = JudgeSettings()
        logfire_config = LogfireConfig.from_settings(settings)
        initialize_logfire_instrumentation(logfire_config)
        logger.info(f"Logfire instrumentation initialized: enabled={logfire_config.enabled}")
    except Exception as e:
        logger.warning(f"Failed to initialize Logfire instrumentation: {e}")


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


def _add_research_tool(
    manager_agent: Agent[None, BaseModel],
    research_agent: Agent[None, BaseModel],
    result_type: type[ResearchResult | ResearchResultSimple | ReviewGenerationResult],
):
    """Add research delegation tool to manager agent.

    Auto-instrumented by logfire.instrument_pydantic_ai() - no manual decorators needed.
    """

    @manager_agent.tool
    async def delegate_research(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None], query: str
    ) -> ResearchResult | ResearchResultSimple | ReviewGenerationResult:
        """Delegate research task to ResearchAgent."""
        # Capture trace data for delegation
        trace_collector = get_trace_collector()
        start_time = time.perf_counter()

        # Log agent-to-agent interaction
        trace_collector.log_agent_interaction(
            from_agent="manager",
            to_agent="researcher",
            interaction_type="delegation",
            data={"query": query, "task_type": "research"},
        )

        # Execute delegation
        result = await research_agent.run(query, usage=ctx.usage)

        # Log tool call with timing
        duration = time.perf_counter() - start_time
        trace_collector.log_tool_call(
            agent_id="manager",
            tool_name="delegate_research",
            success=True,
            duration=duration,
            context="research_delegation",
        )

        if isinstance(
            result.output,
            ResearchResult | ResearchResultSimple | ReviewGenerationResult,
        ):
            return result.output
        return _validate_model_return(str(result.output), result_type)


def _add_analysis_tool(
    manager_agent: Agent[None, BaseModel],
    analysis_agent: Agent[None, BaseModel],
):
    """Add analysis delegation tool to manager agent.

    Auto-instrumented by logfire.instrument_pydantic_ai() - no manual decorators needed.
    """

    @manager_agent.tool
    async def delegate_analysis(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None], query: str
    ) -> AnalysisResult:
        """Delegate analysis task to AnalysisAgent."""
        # Capture trace data for delegation
        trace_collector = get_trace_collector()
        start_time = time.perf_counter()

        # Log agent-to-agent interaction
        trace_collector.log_agent_interaction(
            from_agent="manager",
            to_agent="analyst",
            interaction_type="delegation",
            data={"query": query, "task_type": "analysis"},
        )

        # Execute delegation
        result = await analysis_agent.run(query, usage=ctx.usage)

        # Log tool call with timing
        duration = time.perf_counter() - start_time
        trace_collector.log_tool_call(
            agent_id="manager",
            tool_name="delegate_analysis",
            success=True,
            duration=duration,
            context="analysis_delegation",
        )

        if isinstance(result.output, AnalysisResult):
            return result.output
        return _validate_model_return(str(result.output), AnalysisResult)


def _add_synthesis_tool(
    manager_agent: Agent[None, BaseModel],
    synthesis_agent: Agent[None, BaseModel],
):
    """Add synthesis delegation tool to manager agent.

    Auto-instrumented by logfire.instrument_pydantic_ai() - no manual decorators needed.
    """

    @manager_agent.tool
    async def delegate_synthesis(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None], query: str
    ) -> ResearchSummary:
        """Delegate synthesis task to AnalysisAgent."""
        # Capture trace data for delegation
        trace_collector = get_trace_collector()
        start_time = time.perf_counter()

        # Log agent-to-agent interaction
        trace_collector.log_agent_interaction(
            from_agent="manager",
            to_agent="synthesizer",
            interaction_type="delegation",
            data={"query": query, "task_type": "synthesis"},
        )

        # Execute delegation
        result = await synthesis_agent.run(query, usage=ctx.usage)

        # Log tool call with timing
        duration = time.perf_counter() - start_time
        trace_collector.log_tool_call(
            agent_id="manager",
            tool_name="delegate_synthesis",
            success=True,
            duration=duration,
            context="synthesis_delegation",
        )

        if isinstance(result.output, ResearchSummary):
            return result.output
        return _validate_model_return(str(result.output), ResearchSummary)


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
    if research_agent is not None:
        _add_research_tool(manager_agent, research_agent, result_type)

    if analysis_agent is not None:
        _add_analysis_tool(manager_agent, analysis_agent)

    if synthesis_agent is not None:
        _add_synthesis_tool(manager_agent, synthesis_agent)


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
    max_content_length: int = 15000,
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

    # Determine target agent for PeerRead tools
    # Researcher gets tools in multi-agent mode, manager in single-agent mode
    target_agent = researcher if researcher is not None else manager
    target_agent_id = "researcher" if researcher is not None else "manager"

    # Add PeerRead base tools
    add_peerread_tools_to_agent(target_agent, agent_id=target_agent_id)

    # Add review tools if enabled
    if enable_review_tools:
        from app.tools.peerread_tools import add_peerread_review_tools_to_agent

        add_peerread_review_tools_to_agent(
            target_agent, agent_id=target_agent_id, max_content_length=max_content_length
        )

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
    max_content_length = provider_config.max_content_length or 15000
    manager = _create_manager(prompts, models, provider, enable_review_tools, max_content_length)

    return manager


def _handle_model_http_error(error: ModelHTTPError, provider: str, model_name: str) -> NoReturn:
    """Handle ModelHTTPError with actionable logging. Exits on 429, re-raises otherwise."""
    if error.status_code == 429:
        body = error.body if isinstance(error.body, dict) else {}
        detail = body.get("message") or body.get("details") or str(error)
        logger.error(f"Rate limit exceeded for {provider}({model_name}): {detail}")
        raise SystemExit(1) from error
    logger.error(f"HTTP error from model {provider}({model_name}): {error}")
    raise error


async def run_manager(
    manager: Agent[None, BaseModel],
    query: UserPromptType,
    provider: str,
    usage_limits: UsageLimits | None,
    pydantic_ai_stream: bool = False,
) -> tuple[str, Any]:
    """
    Asynchronously runs the manager with the given query and provider, handling errors
        and printing results.

    Auto-instrumented by logfire.instrument_pydantic_ai() - no manual decorators needed.

    Args:
        manager (Agent): The system agent responsible for running the query.
        query (str): The query to be processed by the manager.
        provider (str): The provider to be used for the query.
        usage_limits (UsageLimits): The usage limits to be applied during the query
            execution.
        pydantic_ai_stream (bool, optional): Flag to enable or disable Pydantic AI
            stream. Defaults to False.
    Returns:
        tuple[str, Any]: Tuple of (execution_id, manager_output) for trace retrieval and evaluation
    """
    # Initialize trace collection
    trace_collector = get_trace_collector()
    execution_id = f"exec_{uuid.uuid4().hex[:12]}"
    trace_collector.start_execution(execution_id)

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

        # Finalize trace collection
        trace_collector.end_execution()
        logger.info(f"Trace collection completed for execution: {execution_id}")

        return execution_id, result.output

    except ModelHTTPError as e:
        trace_collector.end_execution()
        _handle_model_http_error(e, provider, model_name)

    except UsageLimitExceeded as e:
        trace_collector.end_execution()
        logger.error(f"Token limit reached for {provider}({model_name}): {e}")
        raise SystemExit(1) from e

    except Exception as e:
        trace_collector.end_execution()
        logger.error(f"Error in run_manager: {e}")
        raise


def _determine_effective_token_limit(
    token_limit: int | None,
    chat_env_config: AppEnv,
    provider_config: ProviderConfig,
) -> int | None:
    """Determine effective token limit with priority: CLI/GUI > env var > config.

    Args:
        token_limit: Optional CLI/GUI token limit override
        chat_env_config: App environment config with AGENT_TOKEN_LIMIT
        provider_config: Provider config with usage_limits

    Returns:
        Effective token limit or None if not set
    """
    if token_limit is not None:
        return token_limit
    if chat_env_config.AGENT_TOKEN_LIMIT is not None:
        return chat_env_config.AGENT_TOKEN_LIMIT
    return provider_config.usage_limits


def _validate_token_limit(effective_limit: int | None) -> None:
    """Validate token limit bounds (1000-1000000).

    Args:
        effective_limit: Token limit to validate

    Raises:
        ValueError: If limit is outside valid range
    """
    if effective_limit is None:
        return

    if effective_limit < 1000:
        msg = f"Token limit {effective_limit} below minimum 1000"
        logger.error(msg)
        raise ValueError(msg)

    if effective_limit > 1000000:
        msg = f"Token limit {effective_limit} above maximum 1000000"
        logger.error(msg)
        raise ValueError(msg)


def _create_usage_limits(effective_limit: int | None) -> UsageLimits | None:
    """Create UsageLimits object if token limit is set.

    Args:
        effective_limit: Effective token limit

    Returns:
        UsageLimits object or None
    """
    if effective_limit is None:
        return None
    return UsageLimits(request_limit=10, total_tokens_limit=effective_limit)


def setup_agent_env(
    provider: str,
    query: UserPromptType,
    chat_config: ChatConfig | BaseModel,
    chat_env_config: AppEnv,
    token_limit: int | None = None,
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
        token_limit (int | None): Optional token limit override (CLI/GUI param).
            Priority: CLI/GUI > env var > config. Valid range: 1000-1000000.

    Returns:
        EndpointConfig: The configuration object for the agent.
    """

    if not isinstance(chat_config, ChatConfig):
        raise TypeError("'chat_config' of invalid type: ChatConfig expected")

    provider_config = get_provider_config(provider, chat_config.providers)
    prompts = chat_config.prompts
    is_api_key, api_key_msg = get_api_key(provider, chat_env_config)

    # Set up LLM environment with only the selected provider's API key
    selected_meta = PROVIDER_REGISTRY.get(provider)
    if selected_meta and selected_meta.env_key:
        api_keys = {selected_meta.name: getattr(chat_env_config, selected_meta.env_key, "")}
    else:
        api_keys = {}
    setup_llm_environment(api_keys)

    if provider.lower() != "ollama" and not is_api_key:
        msg = f"API key for provider '{provider}' is not set."
        logger.error(msg)
        raise ValueError(msg)

    # Determine and validate token limit with priority: CLI/GUI > env var > config
    effective_limit = _determine_effective_token_limit(
        token_limit, chat_env_config, provider_config
    )
    _validate_token_limit(effective_limit)
    usage_limits = _create_usage_limits(effective_limit)

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
