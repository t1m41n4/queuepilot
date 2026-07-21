from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.db.seed import seed_default_data
from app.db.session import SessionLocal
from app.realtime.router import router as realtime_router
from app.services.assistant import AssistantError
from app.services.queue_engine import QueueEngineError

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(api_router, prefix="/api/v1")
app.include_router(realtime_router)


@app.exception_handler(QueueEngineError)
async def queue_engine_error_handler(request: Request, exc: QueueEngineError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(AssistantError)
async def assistant_error_handler(request: Request, exc: AssistantError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
