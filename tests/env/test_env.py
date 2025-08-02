from pytest import MonkeyPatch

from app.data_models.app_models import AppEnv


def test_app_env_loads_env_vars(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini")
    env = AppEnv()
    assert env.GEMINI_API_KEY == "test-gemini"
