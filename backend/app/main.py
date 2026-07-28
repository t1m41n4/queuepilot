from contextlib import asynccontextmanager
import logging

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

settings = get_settings()
logger = logging.getLogger("queuepilot.api")

@asynccontextmanager
async def lifespan(application: FastAPI):
    db = SessionLocal()
    try:
        seed_default_data(db)
    finally:
        db.close()
    yield


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
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(AssistantError)
async def assistant_error_handler(request: Request, exc: AssistantError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled application error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
