import ollama


def download_ollama_model(model_name):
    """Download a specific Ollama model using the Python API."""

    try:
        ollama.pull(model_name)
        print(f"Successfully downloaded the {model_name} model.")
    except Exception as e:
        print(f"Error downloading the model: {e}")


def chat_with_ollama_model(model_name):
    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "user", "content": "Hello! Can you explain what the Pig Game is?"}
        ],
    )
    print(response["message"]["content"])
    return response
