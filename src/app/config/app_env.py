"""
Application environment settings loaded from environment variables or .env file.

This module uses Pydantic's BaseSettings to manage API keys and configuration
for various inference endpoints, tools, and logging/monitoring services.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(BaseSettings):
    """
    Application environment settings loaded from environment variables or .env file.

    This class uses Pydantic's BaseSettings to manage API keys and configuration
    for various inference endpoints, tools, and logging/monitoring services.
    Environment variables are loaded from a .env file by default.
    """

    # Inference endpoints
    ANTHROPIC_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    FIREWORKS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GITHUB_API_KEY: str = ""
    GROK_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    NEBIUS_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    PERPLEXITY_API_KEY: str = ""
    RESTACK_API_KEY: str = ""
    SAMBANOVA_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""

    # Tools
    TAVILY_API_KEY: str = ""

    # Logging/Monitoring/Tracing
    AGENTOPS_API_KEY: str = ""
    LOGFIRE_API_KEY: str = ""
    WANDB_API_KEY: str = ""

    # Agent Configuration
    AGENT_TOKEN_LIMIT: int | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
