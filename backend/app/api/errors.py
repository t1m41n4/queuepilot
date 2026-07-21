from fastapi import HTTPException, status

from app.services.queue_engine import QueueEngineError


def not_implemented() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


def queue_engine_http_error(error: QueueEngineError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.detail)
