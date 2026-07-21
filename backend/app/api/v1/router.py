from fastapi import APIRouter

from app.api.v1.assistant import router as assistant_router
from app.api.v1.banks import router as banks_router
from app.api.v1.health import router as health_router
from app.api.v1.queue import router as queue_router
from app.api.v1.staff import router as staff_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(banks_router)
api_router.include_router(queue_router)
api_router.include_router(staff_router)
api_router.include_router(assistant_router)
