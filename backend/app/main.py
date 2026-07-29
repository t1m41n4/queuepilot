from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.db.seed import seed_default_data
from app.db.session import SessionLocal
from app.realtime.router import router as realtime_router
from app.services.assistant import AssistantError
from app.services.queue_engine import QueueEngineError
from app.core.config import get_settings
from app.core.observability import (
    elapsed_ms,
    log_event,
    metrics,
    new_request_id,
    reset_request_id,
    set_request_id,
)

settings = get_settings()

@asynccontextmanager
async def lifespan(application: FastAPI):
    log_event("application_startup", environment=settings.environment)
    metrics.increment("application_startups_total")
    db = SessionLocal()
    try:
        log_event("seed_start")
        seed_default_data(db)
        log_event("seed_complete")
    except Exception:
        log_event("startup_initialization_failed", level=logging.ERROR)
        raise
    finally:
        db.close()
    yield
    log_event("application_shutdown")


app = FastAPI(
    title="QueuePilot API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = new_request_id(request.headers.get("X-Request-ID"))
    token = set_request_id(request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
        metrics.increment("http_requests_total")
        log_event(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=elapsed_ms(started),
        )
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        metrics.increment("http_requests_errors_total")
        log_event(
            "http_request_error",
            level=logging.ERROR,
            method=request.method,
            path=request.url.path,
            duration_ms=elapsed_ms(started),
        )
        raise
    finally:
        reset_request_id(token)


@app.middleware("http")
async def security_headers_and_request_limits(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            too_large = int(content_length) > settings.max_request_body_bytes
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})
        if too_large:
            return JSONResponse(status_code=413, content={"detail": "Request body is too large"})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response
app.include_router(api_router, prefix="/api/v1")
app.include_router(realtime_router)


@app.exception_handler(QueueEngineError)
async def queue_engine_error_handler(request: Request, exc: QueueEngineError) -> JSONResponse:
    metrics.increment("queue_operations_errors_total")
    log_event("queue_operation_error", level=logging.WARNING, detail=exc.detail, status_code=exc.status_code)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(AssistantError)
async def assistant_error_handler(request: Request, exc: AssistantError) -> JSONResponse:
    metrics.increment("assistant_errors_total")
    log_event("assistant_error", level=logging.WARNING, detail=exc.detail, status_code=exc.status_code)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    metrics.increment("http_requests_errors_total")
    log_event("unhandled_application_error", level=logging.ERROR, exception_type=type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
