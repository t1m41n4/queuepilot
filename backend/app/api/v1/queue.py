from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import NOT_IMPLEMENTED_RESPONSES
from app.services.queue_engine import QueueEngine
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
    responses={200: {"model": QueueJoinResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def join_queue(request: QueueJoinRequest, db: Session = Depends(get_db)) -> QueueJoinResponse:
    entry = QueueEngine(db).join_queue(request.branch_id, request.customer_name)
    return QueueJoinResponse(
        queue_entry_id=entry.id,
        queue_number=entry.queue_number,
        status=entry.status.value,
        estimated_wait=entry.estimated_wait_minutes or 0,
    )


@router.get(
    "/{queue_entry_id}",
    responses={200: {"model": QueueEntryResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def get_queue_entry(
    queue_entry_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
) -> QueueEntryResponse:
    return QueueEntryResponse(**QueueEngine(db).get_queue_entry(queue_entry_id))


@router.post(
    "/{queue_entry_id}/cancel",
    responses={200: {"model": QueueCancellationResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def cancel_queue_entry(
    queue_entry_id: Annotated[int, Path(ge=1)],
    request: QueueCancellationRequest,
    db: Session = Depends(get_db),
) -> QueueCancellationResponse:
    QueueEngine(db).cancel_queue_entry(queue_entry_id)
    return QueueCancellationResponse(message="Queue cancelled successfully.")
