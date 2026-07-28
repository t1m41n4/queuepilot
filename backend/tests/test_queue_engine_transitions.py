import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.bank import Bank
from app.models.branch import Branch
from app.models.queue import Queue, QueueStatus
from app.models.queue_entry import QueueEntry, QueueEntryStatus
from app.models.queue_event import QueueEvent, QueueEventType
from app.services.queue_engine import InvalidQueueTransitionError, NoEligibleCustomerError, QueueEngine


class QueueEngineTransitionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        bank = Bank(name="Test Bank")
        branch_one = Branch(bank=bank, name="Branch One", average_service_minutes=5)
        branch_two = Branch(bank=bank, name="Branch Two", average_service_minutes=5)
        queue_one = Queue(branch=branch_one, status=QueueStatus.OPEN)
        queue_two = Queue(branch=branch_two, status=QueueStatus.OPEN)
        self.session.add_all([bank, branch_one, branch_two, queue_one, queue_two])
        self.session.commit()
        self.queue_one = queue_one
        self.queue_two = queue_two

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def _entry(self, queue, status):
        entry = QueueEntry(
            queue=queue,
            customer_name="Test Customer",
            queue_number="A001",
            status=status,
            joined_at=datetime.now(timezone.utc),
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    def test_ready_to_checked_in(self):
        entry = self._entry(self.queue_one, QueueEntryStatus.READY)
        self.session.commit()
        result = QueueEngine(self.session).check_in(entry.id)
        self.assertEqual(result.status, QueueEntryStatus.CHECKED_IN)

    def test_call_next_records_one_event_and_requires_service_start(self):
        entry = self._entry(self.queue_one, QueueEntryStatus.CHECKED_IN)
        self.session.commit()
        result = QueueEngine(self.session).call_next(branch_id=self.queue_one.branch_id)
        self.assertEqual(result.id, entry.id)
        events = self.session.scalars(select(QueueEvent).where(QueueEvent.queue_entry_id == entry.id)).all()
        self.assertEqual([event.event_type for event in events], [QueueEventType.CALLED])
        with self.assertRaises(NoEligibleCustomerError):
            QueueEngine(self.session).call_next(branch_id=self.queue_one.branch_id)

    def test_start_service_requires_called_event_and_duplicate_start_is_rejected(self):
        entry = self._entry(self.queue_one, QueueEntryStatus.CHECKED_IN)
        self.session.commit()
        with self.assertRaises(InvalidQueueTransitionError):
            QueueEngine(self.session).start_service(entry.id)
        QueueEngine(self.session).call_next(branch_id=self.queue_one.branch_id)
        result = QueueEngine(self.session).start_service(entry.id)
        self.assertEqual(result.status, QueueEntryStatus.SERVING)
        with self.assertRaises(InvalidQueueTransitionError):
            QueueEngine(self.session).start_service(entry.id)

    def test_complete_service_and_duplicate_completion_are_safe(self):
        entry = self._entry(self.queue_one, QueueEntryStatus.CHECKED_IN)
        self.session.commit()
        QueueEngine(self.session).call_next(branch_id=self.queue_one.branch_id)
        QueueEngine(self.session).start_service(entry.id)
        result = QueueEngine(self.session).complete_service(entry.id)
        self.assertEqual(result.status, QueueEntryStatus.COMPLETED)
        with self.assertRaises(InvalidQueueTransitionError):
            QueueEngine(self.session).complete_service(entry.id)

    def test_branch_targeting_keeps_call_next_on_requested_queue(self):
        first = self._entry(self.queue_one, QueueEntryStatus.CHECKED_IN)
        second = self._entry(self.queue_two, QueueEntryStatus.CHECKED_IN)
        self.session.commit()
        self.assertEqual(QueueEngine(self.session).call_next(branch_id=self.queue_two.branch_id).id, second.id)
        self.assertEqual(QueueEngine(self.session).call_next(branch_id=self.queue_one.branch_id).id, first.id)


if __name__ == "__main__":
    unittest.main()
