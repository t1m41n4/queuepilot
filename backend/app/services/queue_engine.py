from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.branch import Branch
from app.models.queue import Queue, QueueStatus
from app.models.queue_entry import QueueEntry, QueueEntryStatus
from app.models.queue_event import QueueEvent, QueueEventType


class QueueEngineError(Exception):
    status_code = 409

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class QueueNotFoundError(QueueEngineError):
    status_code = 404


class QueueClosedError(QueueEngineError):
    status_code = 409


class InvalidQueueTransitionError(QueueEngineError):
    status_code = 409


class NoEligibleCustomerError(QueueEngineError):
    status_code = 404


class QueueEngine:
    AVERAGE_SERVICE_MINUTES = 5
    READY_THRESHOLD_MINUTES = 10
    ACTIVE_STATUSES = frozenset(
        {
            QueueEntryStatus.WAITING,
            QueueEntryStatus.READY,
            QueueEntryStatus.CHECKED_IN,
        }
    )
    TERMINAL_STATUSES = frozenset(
        {
            QueueEntryStatus.COMPLETED,
            QueueEntryStatus.CANCELLED,
            QueueEntryStatus.SKIPPED,
        }
    )

    def __init__(self, db: Session):
        self.db = db

    def join_queue(self, branch_id: int, customer_name: str) -> QueueEntry:
        queue = self._queue_for_branch(branch_id, lock=True)
        self._require_open(queue)

        next_number = self._next_queue_number(queue.id)
        entry = QueueEntry(
            queue_id=queue.id,
            customer_name=customer_name,
            queue_number=next_number,
            status=QueueEntryStatus.WAITING,
            estimated_wait_minutes=0,
        )
        self.db.add(entry)
        self.db.flush()
        self._record_event(entry, QueueEventType.JOINED)
        self._recalculate_queue(queue)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_queue_entry(self, queue_entry_id: int) -> dict[str, object]:
        entry = self._entry_with_context(queue_entry_id)
        position, estimated_wait = self._position_and_eta(entry, entry.queue.entries)
        return {
            "queue_number": entry.queue_number,
            "branch_name": entry.queue.branch.name,
            "status": entry.status.value,
            "position": position,
            "estimated_wait": estimated_wait,
        }

    def cancel_queue_entry(self, queue_entry_id: int) -> QueueEntry:
        entry = self._entry(queue_entry_id)
        queue = self._require_open(entry.queue)
        self._require_active(entry)
        entry.status = QueueEntryStatus.CANCELLED
        self._record_event(entry, QueueEventType.CANCELLED)
        self._recalculate_queue(queue)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def check_in(self, queue_entry_id: int) -> QueueEntry:
        entry = self._entry(queue_entry_id)
        queue = self._require_open(entry.queue)
        self._require_status(entry, QueueEntryStatus.READY)
        entry.status = QueueEntryStatus.CHECKED_IN
        self._record_event(entry, QueueEventType.CHECKED_IN)
        self._recalculate_queue(queue)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def call_next(self) -> QueueEntry:
        queue = self._single_open_queue(lock=True)
        entry = self.db.scalar(
            select(QueueEntry)
            .where(
                QueueEntry.queue_id == queue.id,
                QueueEntry.status == QueueEntryStatus.CHECKED_IN,
            )
            .order_by(QueueEntry.joined_at, QueueEntry.id)
        )
        if entry is None:
            raise NoEligibleCustomerError("No checked-in customer is available")
        self._record_event(entry, QueueEventType.CALLED)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def start_service(self, queue_entry_id: int) -> QueueEntry:
        entry = self._entry(queue_entry_id)
        queue = self._require_open(entry.queue)
        self._require_status(entry, QueueEntryStatus.CHECKED_IN)
        entry.status = QueueEntryStatus.SERVING
        self._record_event(entry, QueueEventType.SERVICE_STARTED)
        self._recalculate_queue(queue)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def complete_service(self, queue_entry_id: int) -> QueueEntry:
        entry = self._entry(queue_entry_id)
        queue = self._require_open(entry.queue)
        self._require_status(entry, QueueEntryStatus.SERVING)
        entry.status = QueueEntryStatus.COMPLETED
        self._record_event(entry, QueueEventType.SERVICE_COMPLETED)
        self._recalculate_queue(queue)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def skip(self, queue_entry_id: int) -> QueueEntry:
        entry = self._entry(queue_entry_id)
        queue = self._require_open(entry.queue)
        self._require_active(entry)
        entry.status = QueueEntryStatus.SKIPPED
        self._record_event(entry, QueueEventType.SKIPPED)
        self._recalculate_queue(queue)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def pause(self) -> Queue:
        queue = self._single_open_queue(lock=True)
        queue.status = QueueStatus.PAUSED
        self.db.commit()
        self.db.refresh(queue)
        return queue

    def resume(self) -> Queue:
        queue = self.db.scalar(
            select(Queue).where(Queue.status == QueueStatus.PAUSED).order_by(Queue.id).with_for_update()
        )
        if queue is None:
            raise QueueNotFoundError("No paused queue is available")
        queue.status = QueueStatus.OPEN
        self.db.commit()
        self.db.refresh(queue)
        return queue

    def recommend_branch(self) -> Branch:
        queues = list(
            self.db.execute(
                select(Queue)
                .options(joinedload(Queue.branch), joinedload(Queue.entries))
                .where(Queue.status == QueueStatus.OPEN)
                .order_by(Queue.id)
            )
            .unique()
            .scalars()
        )
        if not queues:
            raise QueueNotFoundError("No open queue is available")
        return min(queues, key=lambda queue: (self._queue_eta(queue.entries), queue.branch_id)).branch

    def _queue_for_branch(self, branch_id: int, lock: bool = False) -> Queue:
        statement: Select[tuple[Queue]] = select(Queue).where(Queue.branch_id == branch_id)
        if lock:
            statement = statement.with_for_update()
        queue = self.db.scalar(statement)
        if queue is None:
            raise QueueNotFoundError("Queue not found for branch")
        return queue

    def _single_open_queue(self, lock: bool = False) -> Queue:
        statement: Select[tuple[Queue]] = (
            select(Queue).where(Queue.status == QueueStatus.OPEN).order_by(Queue.id)
        )
        if lock:
            statement = statement.with_for_update()
        queue = self.db.scalar(statement)
        if queue is None:
            raise QueueNotFoundError("No open queue is available")
        return queue

    def _entry(self, queue_entry_id: int) -> QueueEntry:
        entry = self.db.scalar(
            select(QueueEntry).options(joinedload(QueueEntry.queue)).where(QueueEntry.id == queue_entry_id)
        )
        if entry is None:
            raise QueueNotFoundError("Queue entry not found")
        return entry

    def _entry_with_context(self, queue_entry_id: int) -> QueueEntry:
        entry = self.db.execute(
            select(QueueEntry)
            .options(
                joinedload(QueueEntry.queue).joinedload(Queue.branch),
                joinedload(QueueEntry.queue).joinedload(Queue.entries),
            )
            .where(QueueEntry.id == queue_entry_id)
        ).unique().scalar_one_or_none()
        if entry is None:
            raise QueueNotFoundError("Queue entry not found")
        return entry

    def _next_queue_number(self, queue_id: int) -> str:
        count = self.db.scalar(
            select(func.count(QueueEntry.id)).where(QueueEntry.queue_id == queue_id)
        ) or 0
        return f"A{count + 1:03d}"

    def _recalculate_queue(self, queue: Queue) -> None:
        entries = list(
            self.db.scalars(
                select(QueueEntry)
                .where(QueueEntry.queue_id == queue.id)
                .order_by(QueueEntry.joined_at, QueueEntry.id)
            )
        )
        customers_ahead = 0
        for entry in entries:
            if entry.status in self.ACTIVE_STATUSES:
                eta = customers_ahead * self.AVERAGE_SERVICE_MINUTES
                entry.estimated_wait_minutes = eta
                if entry.status == QueueEntryStatus.WAITING and eta <= self.READY_THRESHOLD_MINUTES:
                    entry.status = QueueEntryStatus.READY
                    self._record_event(entry, QueueEventType.READY)
                customers_ahead += 1
            else:
                entry.estimated_wait_minutes = None

    def _queue_eta(self, entries: Sequence[QueueEntry]) -> int:
        return sum(entry.status in self.ACTIVE_STATUSES for entry in entries) * self.AVERAGE_SERVICE_MINUTES

    def _position_and_eta(
        self, entry: QueueEntry, entries: Sequence[QueueEntry]
    ) -> tuple[int, int]:
        if entry.status not in self.ACTIVE_STATUSES:
            return 0, 0
        ahead = 0
        for candidate in sorted(entries, key=lambda item: (item.joined_at, item.id)):
            if candidate.id == entry.id:
                break
            if candidate.status in self.ACTIVE_STATUSES:
                ahead += 1
        return ahead + 1, ahead * self.AVERAGE_SERVICE_MINUTES

    def _record_event(self, entry: QueueEntry, event_type: QueueEventType) -> None:
        self.db.add(QueueEvent(queue_entry_id=entry.id, event_type=event_type))

    def _require_open(self, queue: Queue) -> Queue:
        if queue.status != QueueStatus.OPEN:
            raise QueueClosedError("Queue is not open")
        return queue

    def _require_active(self, entry: QueueEntry) -> None:
        if entry.status not in self.ACTIVE_STATUSES:
            raise InvalidQueueTransitionError("Queue entry is not active")

    def _require_status(self, entry: QueueEntry, expected: QueueEntryStatus) -> None:
        if entry.status != expected:
            raise InvalidQueueTransitionError(
                f"Queue entry must be {expected.value} to perform this operation"
            )
