import ollama
from utils.models import chat_with_ollama_model, download_ollama_model


def test_download_ollama_model():
    """Verify successful download of the llama3.1 model."""

    model_name = "llama3.1"
    download_ollama_model(model_name)
    assert ollama.list()["models"], f"Failed to download {model_name}"


def test_chat_with_ollama_model():
    """Ensure chat functionality works with the llama3.1 model."""

    model_name = "llama3.1"
    response = chat_with_ollama_model(model_name)
    assert (
        "Pig Game" in response["message"]["content"]
    ), "Response should mention Pig Game"
