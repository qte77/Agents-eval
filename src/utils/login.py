"""
This module provides utility functions for managing login state and initializing
the environment for a given project. It includes functionality to load and save
login state, perform a one-time login, and check if the user is logged in.
"""

from agentops import init as ainit
from logfire import configure
from wandb import login as wlogin
from weave import init as wvinit


def login(project_name: str) -> None:
    """
    Logs in to the workspace and initializes the environment for the given project.
    Args:
        project_name (str): The name of the project to initialize.
    Returns:
        None
    """

    try:
        ainit(default_tags=[project_name])
        configure()
        wlogin()
        wvinit(project_name)
    except Exception as e:
        print(e)
        # exit()
