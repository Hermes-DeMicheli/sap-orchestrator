"""Workflow engine core for SAP Orchestrator.

Executes workflow steps sequentially with compensation
support and circuit breaker per system type.
"""

from datetime import datetime
from typing import Optional

from orchestrator.engine.circuit_breaker import CircuitBreaker
from orchestrator.models.workflow import (
    Workflow,
    WorkflowStatus,
    StepStatus,
)


class OrchestratorError(Exception):
    pass


class WorkflowEngine:
    """Executes workflows with resilience patterns."""

    def __init__(self):
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

    def get_circuit_breaker(self, system: str) -> CircuitBreaker:
        if system not in self._circuit_breakers:
            self._circuit_breakers[system] = CircuitBreaker()
        return self._circuit_breakers[system]

    def execute(self, workflow: Workflow) -> WorkflowStatus:
        """Run all steps in order. Compensate on failure."""
        status = WorkflowStatus(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            status=StepStatus.RUNNING,
            steps=workflow.steps,
            created_at=datetime.utcnow(),
        )

        for step in workflow.steps:
            cb = self.get_circuit_breaker(step.system.value)
            if not cb.can_execute():
                step.status = StepStatus.FAILED
                step.error = f"Circuit open for {step.system.value}"
                self._compensate(status)
                break

            step.status = StepStatus.RUNNING
            # Placeholder: actual adapter call goes here
            step.status = StepStatus.COMPLETED
            cb.record_success()

        status.status = StepStatus.COMPLETED
        status.completed_at = datetime.utcnow()
        return status

    def _compensate(self, status: WorkflowStatus):
        """Reverse completed steps in reverse order."""
        for step in reversed(status.steps):
            if step.status == StepStatus.COMPLETED:
                step.status = StepStatus.COMPENSATED