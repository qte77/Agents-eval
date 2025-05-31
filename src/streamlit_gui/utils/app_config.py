from json import dump
from pathlib import Path


def save_config(config):
    """Save configuration to config.json file."""
    config_path = Path(__file__).parent.parent.parent / "config.json"
    with open(config_path, "w") as f:
        dump(config, f, indent=2)
