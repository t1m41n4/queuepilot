from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.queue import Queue
from app.models.queue_entry import QueueEntry
from app.models.staff import Staff
from app.core.observability import log_event, metrics


def require_staff_entry(db: Session, staff: Staff, queue_entry_id: int) -> QueueEntry:
    entry = db.execute(
        select(QueueEntry)
        .options(joinedload(QueueEntry.queue))
        .where(QueueEntry.id == queue_entry_id)
    ).unique().scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")
    if entry.queue.branch_id != staff.branch_id:
        metrics.increment("authorization_failures_total")
        log_event("authorization_failed", level=30, staff_id=staff.id, branch_id=staff.branch_id, resource="queue_entry")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff member is not assigned to this branch")
    return entry


def require_staff_queue(db: Session, staff: Staff) -> Queue:
    queue = db.scalar(select(Queue).where(Queue.branch_id == staff.branch_id))
    if queue is None:
        metrics.increment("authorization_failures_total")
        log_event("authorization_failed", level=30, staff_id=staff.id, branch_id=staff.branch_id, resource="queue")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff member is not assigned to this queue")
    return queue
