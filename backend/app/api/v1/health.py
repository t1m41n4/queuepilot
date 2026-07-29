from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.observability import log_event, metrics
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", response_model=None)
async def readiness_check(db: Session = Depends(get_db)) -> dict[str, str] | JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        metrics.increment("readiness_failures_total")
        log_event("readiness_failed", level=30)
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ready"}


@router.get("/metrics")
async def metrics_snapshot() -> dict[str, object]:
    return {"metrics": metrics.snapshot()}
