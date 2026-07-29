from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any


_request_id: ContextVar[str] = ContextVar("request_id", default="-")
logger = logging.getLogger("uvicorn.error")


class Metrics:
    def __init__(self) -> None:
        self._values: dict[str, int] = {}
        self._lock = threading.Lock()

    def increment(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._values[name] = self._values.get(name, 0) + amount

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._values)


metrics = Metrics()


def new_request_id(value: str | None = None) -> str:
    if value and len(value) <= 64 and all(character.isalnum() or character in "-_." for character in value):
        return value
    return str(uuid.uuid4())


def set_request_id(value: str) -> object:
    return _request_id.set(value)


def reset_request_id(token: object) -> None:
    _request_id.reset(token)  # type: ignore[arg-type]


def current_request_id() -> str:
    return _request_id.get()


def log_event(event: str, level: int = logging.INFO, **fields: Any) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "request_id": current_request_id(),
        **fields,
    }
    logger.log(level, json.dumps(payload, default=str, sort_keys=True))


def elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
