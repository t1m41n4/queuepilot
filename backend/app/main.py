from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(title="QueuePilot API", version="0.1.0", docs_url="/docs", openapi_url="/openapi.json")
app.include_router(api_router, prefix="/api/v1")
