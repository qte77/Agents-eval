import ollama
from requests import get, ConnectionError


def check_server_health():
    """Check if the Ollama server is running and responding."""
    try:
        return get("http://127.0.0.1:11434")
    except ConnectionError as e:
        return e
