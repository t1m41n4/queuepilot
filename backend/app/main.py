from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.services.queue_engine import QueueEngineError

app = FastAPI(title="QueuePilot API", version="0.1.0", docs_url="/docs", openapi_url="/openapi.json")
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(QueueEngineError)
async def queue_engine_error_handler(request: Request, exc: QueueEngineError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
