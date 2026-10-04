"""Pydantic models for SAP Orchestrator."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SystemType(str, Enum):
    ABAP_CLOUD = "abap_cloud"
    BTP = "btp"
    HANA = "hana"
    KYMA = "kyma"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


class WorkflowStep(BaseModel):
    id: str
    system: SystemType
    action: str
    payload: dict
    status: StepStatus = StepStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    retry_count: int = 0


class Workflow(BaseModel):
    workflow_id: str
    name: str
    description: Optional[str] = None
    steps: list[WorkflowStep]
    created_at: datetime


class WorkflowStatus(BaseModel):
    workflow_id: str
    name: str
    status: StepStatus
    steps: list[WorkflowStep]
    created_at: datetime
    completed_at: Optional[datetime] = None