from pytest import MonkeyPatch

from app.utils.load_configs import AppEnv


def test_app_env_loads_env_vars(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini")
    env = AppEnv()
    assert env.GEMINI_API_KEY == "test-gemini"
