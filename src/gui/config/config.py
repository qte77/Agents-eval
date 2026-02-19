"""GUI configuration constants and environment-aware URL resolution."""

import os

APP_CONFIG_PATH = "app/config"
PAGES = ["Home", "Settings", "Prompts", "App", "Evaluation Results", "Agent Graph"]


def resolve_service_url(port: int) -> str:
    """Resolve a service URL for the given port based on the current environment.

    Detection chain (first match wins):
    1. ``PHOENIX_ENDPOINT`` env var — explicit user override
    2. GitHub Codespaces — ``CODESPACE_NAME`` + ``GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN``
    3. Gitpod — ``GITPOD_WORKSPACE_URL``
    4. Fallback — ``http://localhost:{port}``

    Args:
        port (int): The port number the service listens on.

    Returns:
        str: A fully-qualified URL for the service appropriate to the environment.

    Example:
        >>> url = resolve_service_url(6006)
        >>> url.startswith("http")
        True
    """
    # Priority 1: explicit user override
    explicit = os.environ.get("PHOENIX_ENDPOINT")
    if explicit:
        return explicit

    # Priority 2: GitHub Codespaces
    codespace_name = os.environ.get("CODESPACE_NAME")
    codespace_domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
    if codespace_name and codespace_domain:
        return f"https://{codespace_name}-{port}.{codespace_domain}/"

    # Priority 3: Gitpod
    gitpod_url = os.environ.get("GITPOD_WORKSPACE_URL")
    if gitpod_url:
        # Gitpod convention: replace "https://" with "https://{port}-"
        # e.g. https://my-workspace.gitpod.io → https://6006-my-workspace.gitpod.io/
        without_scheme = gitpod_url.removeprefix("https://")
        return f"https://{port}-{without_scheme}/"

    # Priority 4: fallback
    return f"http://localhost:{port}"


PHOENIX_DEFAULT_ENDPOINT = resolve_service_url(6006)
