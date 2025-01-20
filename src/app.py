"""
Module for defining a simple agent and dummy tool using pydantic_ai.
"""

from pydantic_ai import Agent, Tool


class SimpleAgent(Agent):
    """
    A basic agent capable of using tools.
    """

    def use_tool(self, tool_name: str) -> str:
        """
        Execute the specified tool and return its result.
        """

        tool = self.get_tool(tool_name)
        return tool.run()


class DummyTool(Tool):
    """
    A dummy tool that always returns a success message.
    """

    def run(self) -> str:
        """
        Execute the dummy tool and return a success message.
        """

        return "Tool used successfully"
