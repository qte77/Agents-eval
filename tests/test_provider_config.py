from pytest import MonkeyPatch

from app.config.data_models import ProviderConfig


def test_provider_config_parsing(monkeypatch: MonkeyPatch):
    pcfg = ProviderConfig(model_name="foo", base_url="bar")
    assert pcfg.model_name == "foo"
    assert pcfg.base_url == "bar"
