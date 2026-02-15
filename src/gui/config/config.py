from app.evals.settings import JudgeSettings

APP_CONFIG_PATH = "app/config"
PAGES = ["Home", "Settings", "Prompts", "App", "Evaluation Results", "Agent Graph"]
PHOENIX_DEFAULT_ENDPOINT = JudgeSettings().phoenix_endpoint
PROMPTS_DEFAULT = {
    "system_prompt_manager": ("You are a manager overseeing research and analysis tasks..."),
    "system_prompt_researcher": ("You are a researcher. Gather and analyze data..."),
    "system_prompt_analyst": ("You are a research analyst. Use your analytical skills..."),
    "system_prompt_synthesiser": ("You are a research synthesiser. Use your analytical skills..."),
}
