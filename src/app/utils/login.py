"""
This module provides utility functions for managing login state and initializing
the environment for a given project. It includes functionality to load and save
login state, perform a one-time login, and check if the user is logged in.
"""

from os import environ

# from agentops import init as agentops_init  # type: ignore[reportUnknownVariableType]
from logfire import configure as logfire_conf
from wandb import login as wandb_login
from weave import init as weave_init

from app.data_models.app_models import AppEnv
from app.llms.providers import get_api_key
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
        is_api_key, api_key_msg = get_api_key("AGENTOPS", chat_env_config)
        if is_api_key:
            # TODO agentops log to local file
            environ["AGENTOPS_LOGGING_TO_FILE"] = "FALSE"
            agentops_init(
                default_tags=[project_name],
                api_key=api_key_msg,
            )
        is_api_key, api_key_msg = get_api_key("LOGFIRE", chat_env_config)
        if is_api_key:
            logfire_conf(token=api_key_msg)
        is_api_key, api_key_msg = get_api_key("WANDB", chat_env_config)
        if is_api_key:
            wandb_login(key=api_key_msg)
            weave_init(project_name)
    except Exception as e:
        msg = generic_exception(str(e))
        logger.exception(e)
        raise Exception(msg) from e
    finally:
        api_key_msg = ""
