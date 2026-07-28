from fastapi import APIRouter, Depends, HTTPException, Request, status
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
from app.services.staff_authorization import require_staff_entry, require_staff_queue
from app.realtime.publisher import publish_entry_update, publish_queue_status
from app.core.config import get_settings
from app.security.audit import audit_login, audit_staff_action
from app.security.rate_limit import login_rate_limiter


router = APIRouter(prefix="/staff", tags=["staff"])


@router.post(
    "/login",
    response_model=StaffLoginResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Invalid credentials"}},
)
async def staff_login(
    request: StaffLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
) -> StaffLoginResponse:
    settings = get_settings()
    client = http_request.client.host if http_request.client else "unknown"
    rate_key = f"{client}:{request.email.lower()}"
    if not login_rate_limiter.allowed(rate_key, settings.login_rate_limit_attempts, settings.login_rate_limit_window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(settings.login_rate_limit_window_seconds)},
        )
    staff = authenticate_staff(db, request.email, request.password)
    if staff is None:
        audit_login(email=request.email, success=False, client=client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    login_rate_limiter.reset(rate_key)
    audit_login(email=request.email, success=True, client=client)
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
    require_staff_entry(db, current_staff, request.queue_entry_id)
    entry = QueueEngine(db).check_in(request.queue_entry_id)
    audit_staff_action("check_in", staff_id=current_staff.id, branch_id=current_staff.branch_id, success=True)
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
    require_staff_queue(db, current_staff)
    entry = QueueEngine(db).call_next(current_staff.branch_id)
    audit_staff_action("call_next", staff_id=current_staff.id, branch_id=current_staff.branch_id, success=True)
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
    require_staff_entry(db, current_staff, request.queue_entry_id)
    entry = QueueEngine(db).start_service(request.queue_entry_id)
    audit_staff_action("start_service", staff_id=current_staff.id, branch_id=current_staff.branch_id, success=True)
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
    require_staff_entry(db, current_staff, request.queue_entry_id)
    entry = QueueEngine(db).complete_service(request.queue_entry_id)
    audit_staff_action("complete_service", staff_id=current_staff.id, branch_id=current_staff.branch_id, success=True)
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
    require_staff_queue(db, current_staff)
    queue = QueueEngine(db).pause(current_staff.branch_id)
    audit_staff_action("pause", staff_id=current_staff.id, branch_id=current_staff.branch_id, success=True)
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
    require_staff_queue(db, current_staff)
    queue = QueueEngine(db).resume(current_staff.branch_id)
    audit_staff_action("resume", staff_id=current_staff.id, branch_id=current_staff.branch_id, success=True)
    await publish_queue_status(db, queue, "QUEUE_RESUMED")
    return QueueStatusResponse(status="OPEN")
