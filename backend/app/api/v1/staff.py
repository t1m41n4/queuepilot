from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.errors import not_implemented
from app.db.session import get_db
from app.core.security import authenticate_staff, create_access_token, get_current_staff
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
from app.models.staff import Staff
from app.services.queue_engine import QueueEngine


router = APIRouter(prefix="/staff", tags=["staff"])


@router.post(
    "/login",
    response_model=StaffLoginResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Invalid credentials"}},
)
async def staff_login(request: StaffLoginRequest, db: Session = Depends(get_db)) -> StaffLoginResponse:
    staff = authenticate_staff(db, request.email, request.password)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return StaffLoginResponse(
        access_token=create_access_token(staff.email),
        token_type="bearer",
    )


@router.get("/dashboard", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_staff_dashboard(current_staff: Staff = Depends(get_current_staff)) -> None:
    not_implemented()


@router.get("/queue", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_staff_queue(current_staff: Staff = Depends(get_current_staff)) -> None:
    not_implemented()


@router.post(
    "/check-in",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def check_in(
    request: StaffCheckInRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    if isinstance(request, CheckInByQrTokenRequest):
        not_implemented()
    entry = QueueEngine(db).check_in(request.queue_entry_id)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/call-next",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def call_next(
    request: StaffActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    entry = QueueEngine(db).call_next()
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/start-service",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def start_service(
    request: QueueEntryActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    entry = QueueEngine(db).start_service(request.queue_entry_id)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/complete-service",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def complete_service(
    request: QueueEntryActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    entry = QueueEngine(db).complete_service(request.queue_entry_id)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/pause",
    responses={200: {"model": QueueStatusResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def pause_queue(
    request: StaffActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueStatusResponse:
    QueueEngine(db).pause()
    return QueueStatusResponse(status="PAUSED")


@router.post(
    "/resume",
    responses={200: {"model": QueueStatusResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def resume_queue(
    request: StaffActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueStatusResponse:
    QueueEngine(db).resume()
    return QueueStatusResponse(status="OPEN")
