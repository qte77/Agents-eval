from pytest import MonkeyPatch

from app.data_models.app_models import ProviderConfig


def test_provider_config_parsing(monkeypatch: MonkeyPatch):
    pcfg = ProviderConfig.model_validate(
        {"model_name": "foo", "base_url": "https://foo.bar"}
    )
    assert pcfg.model_name == "foo"
    # assert pcfg.base_url == "foo.bar"
