from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.errors import not_implemented
from app.db.session import get_db
from app.core.security import authenticate_staff, create_access_token, get_current_staff
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
from app.schemas.staff_dashboard import StaffDashboardResponse, StaffQueueItemResponse
from app.models.staff import Staff
from app.services.queue_engine import QueueEngine
from app.services.staff_dashboard import StaffDashboard
from app.realtime.publisher import publish_entry_update, publish_queue_status


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


@router.get("/dashboard", response_model=StaffDashboardResponse)
async def get_staff_dashboard(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> StaffDashboardResponse:
    return StaffDashboardResponse(**StaffDashboard(db).summary(current_staff))


@router.get("/queue", response_model=list[StaffQueueItemResponse])
async def get_staff_queue(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> list[StaffQueueItemResponse]:
    return [StaffQueueItemResponse(**entry) for entry in StaffDashboard(db).queue_entries(current_staff)]


@router.post(
    "/check-in",
    response_model=QueueEntryResponse,
)
async def check_in(
    request: StaffCheckInRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    if isinstance(request, CheckInByQrTokenRequest):
        not_implemented()
    entry = QueueEngine(db).check_in(request.queue_entry_id)
    await publish_entry_update(db, entry)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/call-next",
    response_model=QueueEntryResponse,
)
async def call_next(
    request: StaffActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    entry = QueueEngine(db).call_next()
    await publish_entry_update(db, entry, "CALLED")
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/start-service",
    response_model=QueueEntryResponse,
)
async def start_service(
    request: QueueEntryActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    entry = QueueEngine(db).start_service(request.queue_entry_id)
    await publish_entry_update(db, entry)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/complete-service",
    response_model=QueueEntryResponse,
)
async def complete_service(
    request: QueueEntryActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueEntryResponse:
    entry = QueueEngine(db).complete_service(request.queue_entry_id)
    await publish_entry_update(db, entry)
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(entry.id))


@router.post(
    "/pause",
    response_model=QueueStatusResponse,
)
async def pause_queue(
    request: StaffActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueStatusResponse:
    queue = QueueEngine(db).pause()
    await publish_queue_status(db, queue, "QUEUE_PAUSED")
    return QueueStatusResponse(status="PAUSED")


@router.post(
    "/resume",
    response_model=QueueStatusResponse,
)
async def resume_queue(
    request: StaffActionRequest,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff),
) -> QueueStatusResponse:
    queue = QueueEngine(db).resume()
    await publish_queue_status(db, queue, "QUEUE_RESUMED")
    return QueueStatusResponse(status="OPEN")
