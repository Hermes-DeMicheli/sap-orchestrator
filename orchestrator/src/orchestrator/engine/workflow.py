"""Workflow engine core — 2026 best practice.

Sequential execution with:
- per-system circuit breaker
- retry with exponential backoff + jitter
- compensation on failure (Saga pattern)
- structured logging via orchestrator.logging
"""

import asyncio
import time
import random
from datetime import datetime, timezone
from typing import Optional

from orchestrator.engine.circuit_breaker import CircuitBreaker
from orchestrator.models.workflow import (
    Workflow,
    WorkflowStatus,
    StepStatus,
)
from orchestrator.logging import configure_logging

logger = configure_logging("INFO")


class OrchestratorError(Exception):
    pass


class WorkflowEngine:
    """Executes workflows with resilience patterns."""

    def __init__(self, max_retries: int = 3, backoff_seconds: float = 1.0):
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def get_circuit_breaker(self, system: str) -> CircuitBreaker:
        if system not in self._circuit_breakers:
            self._circuit_breakers[system] = CircuitBreaker()
        return self._circuit_breakers[system]

    async def execute(self, workflow: Workflow) -> WorkflowStatus:
        """Run all steps in order. Compensate on failure (Saga pattern)."""
        status = WorkflowStatus(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            status=StepStatus.RUNNING,
            steps=workflow.steps,
            created_at=datetime.now(timezone.utc),
        )

        for step in workflow.steps:
            cb = self.get_circuit_breaker(step.system.value)
            if not cb.can_execute():
                step.status = StepStatus.FAILED
                step.error = f"Circuit open for {step.system.value}"
                logger.warning("circuit_open", extra={"system": step.system.value, "workflow_id": workflow.workflow_id})
                await self._compensate(status)
                break

            step.status = StepStatus.RUNNING
            success = await self._execute_step_with_retry(step)
            if not success:
                step.status = StepStatus.FAILED
                await self._compensate(status)
                break
            cb.record_success()

        status.status = StepStatus.COMPLETED
        status.completed_at = datetime.now(timezone.utc)
        logger.info("workflow_done", extra={"workflow_id": workflow.workflow_id, "status": status.status.value})
        return status

    async def _execute_step_with_retry(self, step) -> bool:
        """Retry with exponential backoff + jitter."""
        for attempt in range(1, self.max_retries + 1):
            try:
                # Placeholder: real adapter call here
                step.status = StepStatus.COMPLETED
                return True
            except Exception as exc:
                step.retry_count = attempt
                logger.warning("step_retry", extra={"step_id": step.id, "attempt": attempt, "error": str(exc)})
                if attempt < self.max_retries:
                    delay = self.backoff_seconds * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                    await asyncio.sleep(delay)
                else:
                    step.error = str(exc)
                    return False
        return False

    async def _compensate(self, status: WorkflowStatus):
        """Reverse completed steps in reverse order (Saga compensation)."""
        for step in reversed(status.steps):
            if step.status == StepStatus.COMPLETED:
                step.status = StepStatus.COMPENSATED
                logger.info("step_compensated", extra={"step_id": step.id})


# Sync convenience wrapper for simple use-cases
def execute_sync(workflow: Workflow) -> WorkflowStatus:
    """Synchronous execute for non-async callers."""
    engine = WorkflowEngine()
    import asyncio as _asyncio
    try:
        loop = _asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Cannot block in async context — raise for caller to await
        raise OrchestratorError("Use execute() in async context")
    return _asyncio.run(engine.execute(workflow))
