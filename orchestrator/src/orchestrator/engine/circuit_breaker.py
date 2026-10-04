"""Circuit breaker for SAP Orchestrator.

Prevents cascading failures by opening the circuit when a
downstream SAP system exceeds the error threshold.
"""

import time
from dataclasses import dataclass, field
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    _failures: int = field(default=0, repr=False)
    _state: CircuitState = field(default=CircuitState.CLOSED, repr=False)
    _last_failure_time: float = field(default=0.0, repr=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
            else:
                return CircuitState.OPEN
        return self._state

    def record_success(self):
        self._failures = 0
        self._state = CircuitState.CLOSED

    def record_failure(self):
        self._failures += 1
        self._last_failure_time = time.monotonic()
        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def can_execute(self) -> bool:
        return self.state != CircuitState.OPEN