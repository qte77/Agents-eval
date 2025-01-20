"""
Tests for starting and checking the status of a local Ollama server.
"""

from utils.ollama import check_server_health
import ollama
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
