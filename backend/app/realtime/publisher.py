from typing import Literal

from sqlalchemy.orm import Session

from app.models.queue import Queue
from app.models.queue_entry import QueueEntry
from app.realtime.manager import connection_manager
from app.services.queue_engine import QueueEngine

SupportedEvent = Literal["QUEUE_UPDATED", "READY", "CALLED", "QUEUE_PAUSED", "QUEUE_RESUMED"]


async def publish_entry_update(
    db: Session,
    entry: QueueEntry,
    event: SupportedEvent = "QUEUE_UPDATED",
) -> None:
    queue = db.get(Queue, entry.queue_id)
    if queue is None:
        return
    state = QueueEngine(db).get_queue_entry(entry.id)
    message = {
        "event": event,
        "branch_id": queue.branch_id,
        "queue_id": queue.id,
        "state": state,
    }
    await connection_manager.broadcast(queue.branch_id, message)
    if event != "QUEUE_UPDATED":
        await connection_manager.broadcast(
            queue.branch_id,
            {**message, "event": "QUEUE_UPDATED"},
        )


async def publish_queue_status(db: Session, queue: Queue, event: Literal["QUEUE_PAUSED", "QUEUE_RESUMED"]) -> None:
    await connection_manager.broadcast(
        queue.branch_id,
        {
            "event": event,
            "branch_id": queue.branch_id,
            "queue_id": queue.id,
            "state": {"status": queue.status.value},
        },
    )
