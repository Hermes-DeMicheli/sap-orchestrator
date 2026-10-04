from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional

app = FastAPI(title="SAP Orchestrator", version="0.1.0")


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


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1)
    steps: list[WorkflowStep]
    description: Optional[str] = None


class WorkflowStatus(BaseModel):
    workflow_id: str
    name: str
    status: StepStatus
    steps: list[WorkflowStep]
    created_at: datetime
    completed_at: Optional[datetime] = None


# In-memory store for demo -- replace with persistent store in production
_workflows: dict[str, WorkflowStatus] = {}


@app.post("/workflows", response_model=WorkflowStatus, status_code=201)
def create_workflow(wf: WorkflowCreate):
    workflow_id = f"wf-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    status = WorkflowStatus(
        workflow_id=workflow_id,
        name=wf.name,
        status=StepStatus.PENDING,
        steps=wf.steps,
        created_at=datetime.utcnow(),
    )
    _workflows[workflow_id] = status
    return status


@app.get("/workflows/{workflow_id}", response_model=WorkflowStatus)
def get_workflow(workflow_id: str):
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _workflows[workflow_id]


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}