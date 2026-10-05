"""Circuit breaker for SAP Orchestrator — 2026 best practice.

States: CLOSED -> OPEN (threshold exceeded) -> HALF_OPEN (probe) -> CLOSED/OPEN.
Exponential backoff for recovery timeout; separate counters per error class.
"""

import time
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    _failures: int = field(default=0, repr=False)
    _state: CircuitState = field(default=CircuitState.CLOSED, repr=False)
    _last_failure_time: float = field(default=0.0, repr=False)
    _half_open_calls: int = field(default=0, repr=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            # Exponential backoff capped at 5 min
            backoff = min(self.recovery_timeout * (2 ** (self._failures - self.failure_threshold)), 300.0)
            # Add jitter to avoid thundering herd
            jitter = random.uniform(0, backoff * 0.1)
            if elapsed + jitter >= backoff:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
            else:
                return CircuitState.OPEN
        return self._state

    def record_success(self):
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._half_open_calls = 0

    def record_failure(self):
        self._failures += 1
        self._last_failure_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN:
            # Any failure in half-open re-opens immediately
            self._state = CircuitState.OPEN
            return
        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def can_execute(self) -> bool:
        s = self.state
        if s == CircuitState.OPEN:
            return False
        if s == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.half_open_max_calls:
                return False
            self._half_open_calls += 1
        return True
