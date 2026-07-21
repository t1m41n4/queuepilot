from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.errors import not_implemented
from app.db.session import get_db
from app.schemas.common import NOT_IMPLEMENTED_RESPONSES
from app.schemas.staff import (
    CheckInByQrTokenRequest,
    QueueEntryActionRequest,
    StaffCheckInRequest,
    StaffLoginRequest,
    StaffLoginResponse,
    StaffActionRequest,
    QueueStatusResponse,
)
from app.schemas.queue import QueueEntryResponse
from app.services.queue_engine import QueueEngine


router = APIRouter(prefix="/staff", tags=["staff"])


@router.post(
    "/login",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={200: {"model": StaffLoginResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def staff_login(request: StaffLoginRequest) -> None:
    not_implemented()


@router.get("/dashboard", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_staff_dashboard() -> None:
    not_implemented()


@router.get("/queue", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_staff_queue() -> None:
    not_implemented()


@router.post(
    "/check-in",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def check_in(request: StaffCheckInRequest, db: Session = Depends(get_db)) -> QueueEntryResponse:
    if isinstance(request, CheckInByQrTokenRequest):
        not_implemented()
    entry = QueueEngine(db).check_in(request.queue_entry_id)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/call-next",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def call_next(request: StaffActionRequest, db: Session = Depends(get_db)) -> QueueEntryResponse:
    entry = QueueEngine(db).call_next()
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/start-service",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def start_service(request: QueueEntryActionRequest, db: Session = Depends(get_db)) -> QueueEntryResponse:
    entry = QueueEngine(db).start_service(request.queue_entry_id)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/complete-service",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def complete_service(request: QueueEntryActionRequest, db: Session = Depends(get_db)) -> QueueEntryResponse:
    entry = QueueEngine(db).complete_service(request.queue_entry_id)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/pause",
    responses={200: {"model": QueueStatusResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def pause_queue(request: StaffActionRequest, db: Session = Depends(get_db)) -> QueueStatusResponse:
    QueueEngine(db).pause()
    return QueueStatusResponse(status="PAUSED")


@router.post(
    "/resume",
    responses={200: {"model": QueueStatusResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def resume_queue(request: StaffActionRequest, db: Session = Depends(get_db)) -> QueueStatusResponse:
    QueueEngine(db).resume()
    return QueueStatusResponse(status="OPEN")
