"""
Tests for starting and checking the status of a local Ollama server.
"""

import json
from utils.ollama import (
    check_server_health,
    get_server_version,
    download_ollama_model,
    chat_with_ollama_model,
)
from pytest import fail
from ollama import list, Response

# "llama3.1" # 4.9 GB, RAM 11.2 GiB
# "phi4" # 9.1 GB, RAM 6.1 GiB
with open("tests/config.json", "r") as config_file:
    config = json.load(config_file)


def test_check_server_health() -> None:
    """Test to check if the Ollama server is running and responding."""

    try:
        response: Response = check_server_health()
        assert response.status_code == 200, (
            "Ollama server is not running or not responding."
        )
    except ConnectionError as e:
        fail(e)


def test_get_server_version() -> None:
    """Test to get the version of the Ollama server."""

    try:
        response: Response = get_server_version()
        assert "version" in response, "Response does not contain expected data."
    except ConnectionError as e:
        fail(e)


def test_download_ollama_model() -> None:
    """Verify successful download of model `config['model_name']`."""

    download_ollama_model(config["model_name"])
    assert list()["models"], f"Failed to download {config['model_name']}"


def test_chat_with_ollama_model() -> None:
    """Ensure chat functionality works with model `config['model_name']`."""

    response: Response = chat_with_ollama_model(
        config["model_name"], config["chat_user_message"]
    )
    assert "Pig Game" in response["message"]["content"], config[
        "chat_expected_contains"
    ]
