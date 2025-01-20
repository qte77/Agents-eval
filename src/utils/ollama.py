from requests import get, ConnectionError


def check_server_health():
    """Check if the Ollama server is running and responding."""
    try:
        return get("http://127.0.0.1:11434")
    except ConnectionError as e:
        return e


def get_server_version():
    """Get the version of the Ollama server."""
    url = "http://localhost:11434/api/version"
    try:
        return get(url).json()
    except ConnectionError as e:
        return e
