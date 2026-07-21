from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.bank import Bank
from app.models.branch import Branch
from app.models.queue import Queue, QueueStatus
from app.services.queue_engine import QueueEngine, QueueNotFoundError


class BankDirectory:
    def __init__(self, db: Session):
        self.db = db

    def banks(self) -> list[Bank]:
        return list(self.db.scalars(select(Bank).order_by(Bank.name)))

    def branches(self, bank_id: int) -> list[dict[str, object]]:
        branches = list(
            self.db.execute(
                select(Branch)
                .options(joinedload(Branch.queue).joinedload(Queue.entries))
                .where(Branch.bank_id == bank_id)
                .order_by(Branch.name)
            )
            .unique()
            .scalars()
        )
        recommended_id: int | None = None
        try:
            recommended_id = QueueEngine(self.db).recommend_branch().id
        except QueueNotFoundError:
            pass

        return [
            {
                "id": branch.id,
                "name": branch.name,
                "estimated_wait": self._estimated_wait(branch.queue),
                "recommended": branch.id == recommended_id,
            }
            for branch in branches
        ]

    @staticmethod
    def _estimated_wait(queue: Queue | None) -> int:
        if queue is None or queue.status != QueueStatus.OPEN:
            return 0
        active = sum(entry.status in QueueEngine.ACTIVE_STATUSES for entry in queue.entries)
        return active * QueueEngine.AVERAGE_SERVICE_MINUTES
