from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.errors import not_implemented
from app.schemas.common import NOT_IMPLEMENTED_RESPONSES
from app.schemas.queue import (
    QueueCancellationRequest,
    QueueCancellationResponse,
    QueueEntryResponse,
    QueueJoinRequest,
    QueueJoinResponse,
)


router = APIRouter(prefix="/queue", tags=["queue"])


@router.post(
    "/join",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={200: {"model": QueueJoinResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def join_queue(request: QueueJoinRequest) -> None:
    not_implemented()


@router.get(
    "/{queue_entry_id}",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def get_queue_entry(
    queue_entry_id: Annotated[int, Path(ge=1)],
) -> None:
    not_implemented()


@router.post(
    "/{queue_entry_id}/cancel",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={200: {"model": QueueCancellationResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def cancel_queue_entry(
    queue_entry_id: Annotated[int, Path(ge=1)],
    request: QueueCancellationRequest,
) -> None:
    not_implemented()
