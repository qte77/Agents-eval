"""
Tests for starting and checking the status of a local Ollama server.
"""

from utils.ollama import check_server_health, get_server_version
from pytest import fail

def test_check_server_health():
    """Test to check if the Ollama server is running and responding."""

    try:
        response = check_server_health()
        assert (
            response.status_code == 200
        ), "Ollama server is not running or not responding."
        print("Ollama server is running and responding correctly.")
    except Exception as e:
        fail(e)


def test_get_server_version():
    """Test to get the version of the Ollama server."""

    try:
        response = get_server_version()
        assert "version" in response, "Response does not contain expected data."
    except ConnectionError as e:
        fail(e)
