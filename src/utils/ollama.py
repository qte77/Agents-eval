"""Utilities for interacting with the Ollama server and models."""

from ollama import chat, pull
from requests import get, ConnectionError
from typing import Union, Dict, Any


def check_server_health() -> Union[Dict[str, Any], ConnectionError]:
    """Check if the Ollama server is running and responding."""
    try:
        return get("http://127.0.0.1:11434")
    except ConnectionError as e:
        return e


def get_server_version() -> Union[Dict[str, Any], ConnectionError]:
    """Get the version of the Ollama server."""
    url = "http://localhost:11434/api/version"
    try:
        return get(url).json()
    except ConnectionError as e:
        return e


def download_ollama_model(model_name: str) -> None:
    """Download a specific Ollama model using the Python API."""
    try:
        pull(model_name)
        print(f"Successfully downloaded the {model_name} model.")
    except Exception as e:
        print(f"Error downloading the model: {e}")


def chat_with_ollama_model(model_name: str, user_message: str) -> Dict[str, Any]:
    """Chat with the specified Ollama model."""
    response = chat(
        model=model_name,
        messages=[{"role": "user", "content": user_message}],
    )
    print(response["message"]["content"])
    return response
