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


def create_agent_with_tool(function: Tool, model_name: str) -> Agent:
    """
    Creates and returns an agent with runtime `model_name` and tool `function` added.
    """

    tool: Tool = Tool(
        name="Roll Die",
        description="Rolls a die and returns a random number between 1 and 6.",
        function=function,
    )
    return Agent(
        model_name,
        deps_type=str,
        system_prompt=(
            "You're a dice game, you should roll the die and only output the resulting number without surrounding. Remember to only output the number without surrounding text for example like this: 1"
        ),
        tools=[tool],
    )
