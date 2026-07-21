from fastapi import APIRouter, status

from app.api.errors import not_implemented
from app.schemas.common import NOT_IMPLEMENTED_RESPONSES
from app.schemas.staff import (
    QueueEntryActionRequest,
    StaffActionRequest,
    StaffCheckInRequest,
    StaffLoginRequest,
    StaffLoginResponse,
)


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
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses=NOT_IMPLEMENTED_RESPONSES,
)
async def check_in(request: StaffCheckInRequest) -> None:
    not_implemented()


@router.post(
    "/call-next",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses=NOT_IMPLEMENTED_RESPONSES,
)
async def call_next(request: StaffActionRequest) -> None:
    not_implemented()


@router.post(
    "/start-service",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses=NOT_IMPLEMENTED_RESPONSES,
)
async def start_service(request: QueueEntryActionRequest) -> None:
    not_implemented()


@router.post(
    "/complete-service",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses=NOT_IMPLEMENTED_RESPONSES,
)
async def complete_service(request: QueueEntryActionRequest) -> None:
    not_implemented()


@router.post(
    "/pause",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses=NOT_IMPLEMENTED_RESPONSES,
)
async def pause_queue(request: StaffActionRequest) -> None:
    not_implemented()


@router.post(
    "/resume",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses=NOT_IMPLEMENTED_RESPONSES,
)
async def resume_queue(request: StaffActionRequest) -> None:
    not_implemented()
