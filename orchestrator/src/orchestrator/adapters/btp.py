"""BTP adapter for SAP Orchestrator.

Connects to BTP services via Destinations, handles service bindings
and secret retrieval from the BTP Secret Store.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BtpServiceConfig:
    service_name: str
    service_plan: str
    binding_name: str
    credentials: Optional[dict] = None


@dataclass
class BtpResponse:
    success: bool
    message: str
    data: Optional[dict] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


def invoke_btp_service(config: BtpServiceConfig, payload: dict) -> BtpResponse:
    """Invoke a BTP service via destination.

    Placeholder -- in production this resolves the destination,
    obtains an OAuth2 token, and calls the service endpoint.
    """
    return BtpResponse(
        success=True,
        message=f"Service {config.service_name} invoked",
        data={"service": config.service_name, "payload": payload},
    )