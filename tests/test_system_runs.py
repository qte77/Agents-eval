def test_agent_existence():
    agent = SimpleAgent()
    assert isinstance(agent, Agent), "Agent should be created successfully"


def test_agent_tool_usage():
    agent = SimpleAgent()
    tool = DummyTool(name="dummy_tool")
    agent.add_tool(tool)

    result = agent.use_tool("dummy_tool")
    assert result == "Tool used successfully", "Agent should be able to use the tool"
