import os

import pytest
from sqlalchemy import create_engine, text


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL is not configured")
def test_postgres_schema_and_seed_data():
    engine = create_engine(os.environ["TEST_DATABASE_URL"])
    with engine.connect() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
        }
        assert {"banks", "branches", "queues", "queue_entries", "queue_events", "staff"} <= tables
        assert connection.execute(text("SELECT count(*) FROM banks")).scalar_one() >= 1
        assert connection.execute(text("SELECT count(*) FROM branches")).scalar_one() >= 2
        assert connection.execute(text("SELECT count(*) FROM queues")).scalar_one() >= 2
        assert connection.execute(text("SELECT count(*) FROM staff")).scalar_one() >= 2
