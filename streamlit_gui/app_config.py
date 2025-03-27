from json import dump, load
from pathlib import Path


def load_app_config():
    """Load configuration from config.json file."""
    config_path = Path(__file__) / "src" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return load(f)
    return {
        "providers": ["Provider A", "Provider B", "Provider C"],
        "include_a": False,
        "include_b": False,
        "prompts": {
            "system_prompt_manager": (
                "You are a manager overseeing research and analysis tasks. Your role "
                "is to coordinate the efforts of the research and analysis agents to "
                "provide comprehensive answers to user queries."
            ),
            "system_prompt_researcher": (
                "You are a researcher. Gather and analyze data relevant to the topic. "
                "Use the search tool to gather data. Always check accuracy of "
                "assumptions, facts, and conclusions. Synthesize your research it into "
                "a concise summary."
            ),
            "system_prompt_analyst": (
                "You are a research analyst. Use your analytical skills to check the "
                "accuracy of assumptions, facts, and conclusions in the data provided. "
                "If you approve of the data provided respond with a positive "
                "acknowledgment. Otherwise provide feedback and return it."
            ),
        },
        "streamed_output": False,
    }


def save_config(config):
    """Save configuration to config.json file."""
    config_path = Path(__file__).parent.parent.parent / "config.json"
    with open(config_path, "w") as f:
        dump(config, f, indent=2)
