import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Bank, Branch, Queue, QueueStatus, Staff
from app.core.security import hash_password


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = Session(engine)
    bank = Bank(name="Test Bank")
    cbd = Branch(bank=bank, name="CBD", average_service_minutes=5)
    westlands = Branch(bank=bank, name="Westlands", average_service_minutes=5)
    session.add_all([
        bank,
        cbd,
        westlands,
        Queue(branch=cbd, status=QueueStatus.OPEN),
        Queue(branch=westlands, status=QueueStatus.OPEN),
        Staff(branch=cbd, full_name="CBD Staff", email="cbd@test.local", password_hash=hash_password("password123")),
        Staff(branch=westlands, full_name="Westlands Staff", email="westlands@test.local", password_hash=hash_password("password123")),
    ])
    session.commit()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    session.close()
    engine.dispose()
