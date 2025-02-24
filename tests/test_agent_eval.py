"""
Tests for evaluating a Pydantic-AI agent.
"""

import json
from pydantic_ai import Agent
from pydantic_ai.result import RunResult
from utils.agents import create_agent_with_tool
from utils.eval import evaluate_agent_response
from utils.tools import roll_die  # , get_player_name


with open("tests/config.json", "r") as config_file:
    config = json.load(config_file)


def test_evaluate_agent_response():
    """
    Test the evaluation of an agent's response for correctness, relevance, coherence, politeness, and tool usage.
    """

    agent: Agent = create_agent_with_tool(roll_die, config["model_name_full"])
    result: RunResult = agent.run_sync("1")
    metrics = evaluate_agent_response(result)

    assert print(result)

    # Assert that the response contains the expected data
    assert metrics["correctness"] == 1, "Response does not contain expected data."
    assert metrics["relevance"] == 1, "Response is not relevant to the query."
    assert metrics["coherence"] == 1, "Response is not coherent."
    assert metrics["politeness"] == 1, "Response is not polite."

    # Assert that the tool was used correctly
    assert metrics["tool_usage"] == 1, "Tool 'Roll Die' was not used correctly."
