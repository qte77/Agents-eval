"""
Tests for starting and checking the status of a local Ollama server.
"""

from typing import Any, Dict
from utils.ollama import (
    check_server_health,
    get_server_version,
    download_ollama_model,
    chat_with_ollama_model,
)
from pytest import fail
from ollama import list

# "llama3.1" # 4.9 GB, RAM 11.2 GiB
# "phi4" # 9.1 GB, RAM 6.1 GiB
MODEL_NAME: str = "llama3.1"


def test_check_server_health() -> None:
    """Test to check if the Ollama server is running and responding."""

    try:
        response: Dict[str, Any] = check_server_health()
        assert (
            response.status_code == 200
        ), "Ollama server is not running or not responding."
    except ConnectionError as e:
        fail(e)


def test_get_server_version() -> None:
    """Test to get the version of the Ollama server."""

    try:
        response: Dict[str, Any] = get_server_version()
        assert "version" in response, "Response does not contain expected data."
    except ConnectionError as e:
        fail(e)


def test_download_ollama_model() -> None:
    """Verify successful download of model `MODEL_NAME`."""

    download_ollama_model(MODEL_NAME)
    assert list()["models"], f"Failed to download {MODEL_NAME}"


def test_chat_with_ollama_model() -> None:
    """Ensure chat functionality works with model `MODEL_NAME`."""

    user_message: str = "Hello! Can you explain what the Pig Game is?"
    response: Dict[str, Any] = chat_with_ollama_model(MODEL_NAME, user_message)
    assert (
        "Pig Game" in response["message"]["content"]
    ), "Response should mention Pig Game"
