"""Retry utility — exponential backoff + jitter (2026 best practice)."""

import asyncio
import random
from typing import Callable, TypeVar

T = TypeVar("T")


async def with_retry(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Execute func with exponential backoff + jitter.

    Formula: delay = min(base * 2^(attempt-1) + jitter, max_delay)
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as exc:
            if not isinstance(exc, retry_on):
                raise
            last_exc = exc
            if attempt < max_retries:
                delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                delay += random.uniform(0, delay * 0.1)  # jitter
                await asyncio.sleep(delay)
    raise last_exc  # type: ignore[misc]
