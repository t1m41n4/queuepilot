from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_default_data
from app.models import Bank, Branch, Queue, Staff


def test_seed_is_deterministic_and_complete():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_default_data(session)
        seed_default_data(session)
        assert session.scalar(select(func.count()).select_from(Bank)) == 1
        assert session.scalar(select(func.count()).select_from(Branch)) == 2
        assert session.scalar(select(func.count()).select_from(Queue)) == 2
        assert session.scalar(select(func.count()).select_from(Staff)) == 2
