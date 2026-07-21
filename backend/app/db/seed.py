from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.bank import Bank
from app.models.branch import Branch
from app.models.queue import Queue, QueueStatus
from app.models.staff import Staff


DEMO_BANK_NAME = "QueuePilot Demo Bank"
DEMO_BRANCHES = ("QueuePilot CBD", "QueuePilot Westlands")
DEFAULT_STAFF_EMAIL = "staff@queuepilot.local"
DEFAULT_STAFF_PASSWORD = "password123"


def seed_default_data(db: Session) -> None:
    bank = db.scalar(select(Bank).where(Bank.name == DEMO_BANK_NAME))
    if bank is None:
        bank = Bank(name=DEMO_BANK_NAME)
        db.add(bank)
        db.flush()

    branches: list[Branch] = []
    for branch_name in DEMO_BRANCHES:
        branch = db.scalar(
            select(Branch).where(Branch.bank_id == bank.id, Branch.name == branch_name)
        )
        if branch is None:
            branch = Branch(
                bank_id=bank.id,
                name=branch_name,
                average_service_minutes=5,
            )
            db.add(branch)
            db.flush()
        branches.append(branch)

        queue = db.scalar(select(Queue).where(Queue.branch_id == branch.id))
        if queue is None:
            db.add(Queue(branch_id=branch.id, status=QueueStatus.OPEN))

    db.flush()
    staff = db.scalar(select(Staff).where(Staff.email == DEFAULT_STAFF_EMAIL))
    if staff is None:
        db.add(
            Staff(
                branch_id=branches[0].id,
                full_name="QueuePilot Demo Staff",
                email=DEFAULT_STAFF_EMAIL,
                password_hash=hash_password(DEFAULT_STAFF_PASSWORD),
            )
        )
    db.commit()
