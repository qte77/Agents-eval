# from pydantic_ai import Agent, Tool
from pydantic_ai.result import RunResult
from typing import Dict, Any
# from pytest import fail


def evaluate_agent_response(result: RunResult) -> Dict[str, Any]:
    """
    Evaluate the agent's response based on custom metrics.

    :param result: The result of the agent's run.
    :return: A dictionary containing evaluation metrics.
    """

    metrics = {
        "correctness": 0,
        "relevance": 0,
        "coherence": 0,
        "politeness": 0,
        "tool_usage": 0,
    }

    # Check if the response contains the expected data
    if "message" in result.data and "content" in result.data["message"]:
        metrics["correctness"] = (
            1 if "Pig Game" in result.data["message"]["content"] else 0
        )
        metrics["relevance"] = (
            1 if "Pig Game" in result.data["message"]["content"] else 0
        )
        metrics["coherence"] = (
            1 if len(result.data["message"]["content"].split()) > 10 else 0
        )
        metrics["politeness"] = (
            1 if "please" in result.data["message"]["content"].lower() else 0
        )

    # Check if the tool was used correctly
    if result.tool_calls:
        metrics["tool_usage"] = (
            1 if any(call.name == "Roll Die" for call in result.tool_calls) else 0
        )

    return metrics
