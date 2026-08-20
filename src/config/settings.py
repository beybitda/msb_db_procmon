"""Application configuration, loaded once from environment variables.

Keeping this in one place means no module ever calls ``os.getenv`` directly,
and credentials never appear hardcoded in source files.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class OracleSettings:
    """Oracle connection parameters, sourced from the environment."""

    user: str
    password: str
    host: str
    port: str
    service_name: str

    @property
    def is_configured(self) -> bool:
        """True only if every credential needed to connect is present."""
        return all([self.user, self.password, self.host, self.service_name])

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service_name}"

    @property
    def display_target(self) -> str:
        """Human-readable connection string safe to show in the UI (no password)."""
        return f"{self.user}@{self.host}:{self.port}/{self.service_name}"


@dataclass(frozen=True)
class AppSettings:
    """General app-level configuration."""

    page_title: str = "Process Monitor"
    page_icon: str = "⬡"
    cache_ttl_seconds: int = 30
    demo_row_count: int = 300
    auto_refresh_seconds: int = 30
    table_name: str = "ANALYST_MSB2.MSB_DB_PROCESS_MONITOR"


def get_oracle_settings() -> OracleSettings:
    """Read Oracle credentials from the environment (called once per session)."""
    return OracleSettings(
        user=os.getenv("ORACLE_USER", ""),
        password=os.getenv("ORACLE_PASS", ""),
        host=os.getenv("ORACLE_HOST", ""),
        port=os.getenv("ORACLE_PORT", "1521"),
        service_name=os.getenv("ORACLE_DB", ""),
    )


def get_app_settings() -> AppSettings:
    return AppSettings()
