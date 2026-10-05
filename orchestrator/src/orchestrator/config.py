"""Configuration via environment variables — 12-factor app pattern."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    """Centralised config; all values come from env with sane defaults."""

    app_title: str = "SAP Orchestrator"
    app_version: str = "0.2.0-beta"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    otel_endpoint: Optional[str] = None
    hana_conn_str: Optional[str] = None
    btp_dest_url: Optional[str] = None
    abap_cloud_url: Optional[str] = None
    circuit_failure_threshold: int = 5
    circuit_recovery_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            app_title=os.getenv("ORCHESTRATOR_TITLE", "SAP Orchestrator"),
            app_version=os.getenv("ORCHESTRATOR_VERSION", "0.2.0-beta"),
            host=os.getenv("ORCHESTRATOR_HOST", "0.0.0.0"),
            port=int(os.getenv("ORCHESTRATOR_PORT", "8000")),
            log_level=os.getenv("ORCHESTRATOR_LOG_LEVEL", "INFO"),
            otel_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            hana_conn_str=os.getenv("HANA_CONN_STR"),
            btp_dest_url=os.getenv("BTP_DEST_URL"),
            abap_cloud_url=os.getenv("ABAP_CLOUD_URL"),
            circuit_failure_threshold=int(
                os.getenv("CIRCUIT_FAILURE_THRESHOLD", "5")
            ),
            circuit_recovery_seconds=float(
                os.getenv("CIRCUIT_RECOVERY_SECONDS", "30")
            ),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_backoff_seconds=float(
                os.getenv("RETRY_BACKOFF_SECONDS", "1")
            ),
        )


config = AppConfig.from_env()