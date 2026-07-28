import os
import threading
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.bank import Bank
from app.models.branch import Branch
from app.models.queue import Queue, QueueStatus
from app.models.queue_entry import QueueEntry
from app.services.queue_engine import QueueEngine


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL is required")
def test_concurrent_join_is_serialized_by_postgres() -> None:
    engine = create_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    branch_id: int
    with SessionLocal() as db:
        suffix = uuid4().hex
        bank = Bank(name=f"Concurrency Test Bank {suffix}")
        db.add(bank)
        db.flush()
        branch = Branch(bank_id=bank.id, name=f"Concurrency Test Branch {suffix}", average_service_minutes=5)
        db.add(branch)
        db.flush()
        queue = Queue(branch_id=branch.id, status=QueueStatus.OPEN)
        db.add(queue)
        db.flush()
        db.commit()
        branch_id = branch.id

    barrier = threading.Barrier(2)
    results: list[str] = []
    errors: list[Exception] = []

    def call_next() -> None:
        try:
            with SessionLocal() as db:
                barrier.wait(timeout=10)
                entry = QueueEngine(db).join_queue(branch_id, "Concurrent Customer")
                results.append(entry.queue_number)
        except Exception as exc:  # captured for assertion in the test thread
            errors.append(exc)

    threads = [threading.Thread(target=call_next) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)

    assert len(results) == 2
    assert not errors
    assert len(set(results)) == 2

    with SessionLocal() as db:
        queue_id = db.scalar(select(Queue.id).where(Queue.branch_id == branch_id))
        entries = db.scalars(select(QueueEntry).where(QueueEntry.queue_id == queue_id)).all()
        assert len(entries) == 2
        assert len({entry.queue_number for entry in entries}) == 2
    engine.dispose()
