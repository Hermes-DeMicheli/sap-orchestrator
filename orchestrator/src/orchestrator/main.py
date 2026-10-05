from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from orchestrator.config import config
from orchestrator.logging import configure_logging
import logging

logger = configure_logging(config.log_level)

app = FastAPI(title=config.app_title, version=config.app_version)


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
    name: str = Field(..., min_length=1, max_length=200)
    steps: list[WorkflowStep]
    description: Optional[str] = Field(None, max_length=1000)


class WorkflowStatus(BaseModel):
    workflow_id: str
    name: str
    status: StepStatus
    steps: list[WorkflowStep]
    created_at: datetime
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    checks: dict[str, str]


# In-memory store for demo -- replace with persistent store in production
_workflows: dict[str, WorkflowStatus] = {}


@app.get("/health", response_model=HealthResponse)
def health():
    """Liveness + readiness probe."""
    checks: dict[str, str] = {"engine": "ok"}
    overall = "ok"
    if config.hana_conn_str is None:
        checks["hana"] = "unconfigured"
    else:
        checks["hana"] = "configured"
    if config.abap_cloud_url is None:
        checks["abap_cloud"] = "unconfigured"
    else:
        checks["abap_cloud"] = "configured"
    if any(v == "unconfigured" for v in checks.values()):
        overall = "degraded"
    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": config.app_version,
        "checks": checks,
    }


@app.post("/workflows", response_model=WorkflowStatus, status_code=201)
def create_workflow(wf: WorkflowCreate):
    """Create a new workflow with validation."""
    if not wf.steps:
        raise HTTPException(status_code=422, detail="Workflow must have at least one step")
    if len(wf.steps) > 50:
        raise HTTPException(status_code=422, detail="Workflow cannot exceed 50 steps")

    workflow_id = f"wf-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    status = WorkflowStatus(
        workflow_id=workflow_id,
        name=wf.name,
        status=StepStatus.PENDING,
        steps=wf.steps,
        created_at=datetime.now(timezone.utc),
    )
    _workflows[workflow_id] = status
    logger.info("workflow_created", extra={"wf_id": workflow_id, "wf_name": wf.name, "wf_steps": len(wf.steps)})
    return status


@app.get("/workflows/{workflow_id}", response_model=WorkflowStatus)
def get_workflow(workflow_id: str):
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _workflows[workflow_id]


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("http_error", extra={"path": request.url.path, "status": exc.status_code, "detail": exc.detail})
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "path": request.url.path})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", extra={"path": request.url.path, "error": str(exc)}, exc_info=True)
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "path": request.url.path})
