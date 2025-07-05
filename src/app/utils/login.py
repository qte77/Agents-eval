"""
This module provides utility functions for managing login state and initializing
the environment for a given project. It includes functionality to load and save
login state, perform a one-time login, and check if the user is logged in.
"""

from os import environ

from agentops import init as agentops_init
from logfire import configure as logfire_conf
from wandb import login as wandb_login
from weave import init as weave_init

from app.agents.llm_model_funs import get_api_key
from app.config.data_models import AppEnv
from app.utils.error_messages import generic_exception
from app.utils.log import logger


def login(project_name: str, chat_env_config: AppEnv):
    """
    Logs in to the workspace and initializes the environment for the given project.
    Args:
        project_name (str): The name of the project to initialize.
        chat_env_config (AppEnv): The application environment configuration
            containing the API keys.
    Returns:
        None
    """

    try:
        logger.info(f"Logging in to the workspaces for project: {project_name}")
        environ["AGENTOPS_LOGGING_TO_FILE"] = "FALSE"
        agentops_init(
            default_tags=[project_name],
            api_key=get_api_key("AGENTOPS", chat_env_config),
        )
        logfire_conf(token=get_api_key("LOGFIRE", chat_env_config))
        wandb_login(key=get_api_key("WANDB", chat_env_config))
        weave_init(project_name)
    except Exception as e:
        msg = generic_exception(str(e))
        logger.exception(e)
        raise Exception(msg) from e
