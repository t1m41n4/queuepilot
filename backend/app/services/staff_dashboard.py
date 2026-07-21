from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.queue import Queue
from app.models.queue_entry import QueueEntry, QueueEntryStatus
from app.models.staff import Staff
from app.services.queue_engine import QueueEngine


class StaffDashboard:
    def __init__(self, db: Session):
        self.db = db

    def summary(self, staff: Staff) -> dict[str, object]:
        queue = self._queue_for_staff(staff)
        entries = self._ordered_entries(queue)
        serving = next((entry for entry in entries if entry.status == QueueEntryStatus.SERVING), None)
        return {
            "branch_id": staff.branch_id,
            "queue_status": queue.status.value if queue else "CLOSED",
            "waiting": sum(entry.status == QueueEntryStatus.WAITING for entry in entries),
            "ready": sum(entry.status == QueueEntryStatus.READY for entry in entries),
            "checked_in": sum(entry.status == QueueEntryStatus.CHECKED_IN for entry in entries),
            "current_customer": serving.customer_name if serving else None,
        }

    def queue_entries(self, staff: Staff) -> list[dict[str, object]]:
        queue = self._queue_for_staff(staff)
        entries = self._ordered_entries(queue)
        call_next_id = next(
            (entry.id for entry in entries if entry.status == QueueEntryStatus.CHECKED_IN),
            None,
        )
        return [
            {
                "queue_entry_id": entry.id,
                "queue_number": entry.queue_number,
                "customer_name": entry.customer_name,
                "status": entry.status.value,
                "estimated_wait": entry.estimated_wait_minutes,
                "action": self._action_for(entry, call_next_id),
            }
            for entry in entries
            if entry.status in QueueEngine.ACTIVE_STATUSES or entry.status == QueueEntryStatus.SERVING
        ]

    def _queue_for_staff(self, staff: Staff) -> Queue | None:
        return self.db.execute(
            select(Queue)
            .options(joinedload(Queue.entries))
            .where(Queue.branch_id == staff.branch_id)
        ).unique().scalar_one_or_none()

    @staticmethod
    def _ordered_entries(queue: Queue | None) -> list[QueueEntry]:
        if queue is None:
            return []
        return sorted(queue.entries, key=lambda entry: (entry.joined_at, entry.id))

    @staticmethod
    def _action_for(entry: QueueEntry, call_next_id: int | None) -> str | None:
        if entry.status == QueueEntryStatus.READY:
            return "Check In"
        if entry.status == QueueEntryStatus.CHECKED_IN and entry.id == call_next_id:
            return "Call Next"
        if entry.status == QueueEntryStatus.SERVING:
            return "Complete Service"
        return None
