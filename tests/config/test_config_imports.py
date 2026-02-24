"""Tests verifying LogfireConfig and PeerReadConfig live in src/app/config/.

These tests are written BEFORE the new files exist (RED phase) to confirm
that the new canonical import paths work after migration.
"""

from app.config import LogfireConfig, PeerReadConfig


def test_logfire_config_importable_from_config_package():
    """LogfireConfig must be importable from app.config."""
    assert LogfireConfig is not None


def test_peerread_config_importable_from_config_package():
    """PeerReadConfig must be importable from app.config."""
    assert PeerReadConfig is not None


def test_logfire_config_module_path():
    """LogfireConfig must originate from app.config.logfire_config."""
    assert LogfireConfig.__module__ == "app.config.logfire_config"


def test_peerread_config_module_path():
    """PeerReadConfig must originate from app.config.peerread_config."""
    assert PeerReadConfig.__module__ == "app.config.peerread_config"


def test_logfire_config_direct_import():
    """LogfireConfig must be directly importable from app.config.logfire_config."""
    from app.config.logfire_config import LogfireConfig as LFC  # noqa: PLC0415

    assert LFC is LogfireConfig


def test_peerread_config_direct_import():
    """PeerReadConfig must be directly importable from app.config.peerread_config."""
    from app.config.peerread_config import PeerReadConfig as PRC  # noqa: PLC0415

    assert PRC is PeerReadConfig
