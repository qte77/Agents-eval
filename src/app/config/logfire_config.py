"""Logfire + Phoenix tracing configuration model."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.config.judge_settings import JudgeSettings

from pydantic import BaseModel


class LogfireConfig(BaseModel):
    """Configuration for Logfire + Phoenix tracing integration.

    Constructed from JudgeSettings via from_settings(). All values
    are controlled by JUDGE_LOGFIRE_* and JUDGE_PHOENIX_* env vars
    through pydantic-settings.
    """

    enabled: bool = True
    send_to_cloud: bool = False
    phoenix_endpoint: str = "http://localhost:6006"
    service_name: str = "peerread-evaluation"

    @classmethod
    def from_settings(cls, settings: JudgeSettings) -> LogfireConfig:
        """Create LogfireConfig from JudgeSettings.

        Args:
            settings: JudgeSettings instance with logfire fields.

        Returns:
            LogfireConfig populated from pydantic-settings.
        """
        return cls(
            enabled=settings.logfire_enabled,
            send_to_cloud=settings.logfire_send_to_cloud,
            phoenix_endpoint=settings.phoenix_endpoint,
            service_name=settings.logfire_service_name,
        )
