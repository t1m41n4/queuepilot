import unittest

from fastapi import HTTPException

from app.models.queue import Queue, QueueStatus
from app.models.queue_entry import QueueEntry
from app.models.staff import Staff
from app.services.staff_authorization import require_staff_entry, require_staff_queue


class _Result:
    def __init__(self, value):
        self.value = value

    def unique(self):
        return self

    def scalar_one_or_none(self):
        return self.value


class _Session:
    def __init__(self, *, entry=None, queue=None):
        self.entry = entry
        self.queue = queue

    def execute(self, _statement):
        return _Result(self.entry)

    def scalar(self, _statement):
        return self.queue


class StaffAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.staff = Staff(id=1, branch_id=10, full_name="CBD Staff", email="staff@example.test", password_hash="hash")
        self.queue = Queue(id=1, branch_id=10, status=QueueStatus.OPEN)
        self.entry = QueueEntry(id=5, queue_id=1, queue=self.queue)

    def test_staff_can_access_assigned_queue_and_entry(self):
        session = _Session(entry=self.entry, queue=self.queue)
        self.assertIs(require_staff_entry(session, self.staff, 5), self.entry)
        self.assertIs(require_staff_queue(session, self.staff), self.queue)

    def test_cross_branch_entry_is_forbidden(self):
        other_queue = Queue(id=2, branch_id=20, status=QueueStatus.OPEN)
        entry = QueueEntry(id=6, queue_id=2, queue=other_queue)
        with self.assertRaises(HTTPException) as context:
            require_staff_entry(_Session(entry=entry), self.staff, 6)
        self.assertEqual(context.exception.status_code, 403)

    def test_missing_branch_queue_is_forbidden(self):
        with self.assertRaises(HTTPException) as context:
            require_staff_queue(_Session(queue=None), self.staff)
        self.assertEqual(context.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
