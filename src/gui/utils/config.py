from pathlib import Path

APP_PATH = Path(__file__).parent / "app"
PAGES = ["Home", "Settings", "Prompts", "App"]
PROMPTS_DEFAULT = {
    "system_prompt_manager": (
        "You are a manager overseeing research and analysis tasks..."
    ),
    "system_prompt_researcher": ("You are a researcher. Gather and analyze data..."),
    "system_prompt_analyst": (
        "You are a research analyst. Use your analytical skills..."
    ),
    "system_prompt_synthesiser": (
        "You are a research synthesiser. Use your analytical skills..."
    ),
}
