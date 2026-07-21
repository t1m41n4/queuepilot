from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.queue_entry import QueueEntry


class QueueEventType(str, Enum):
    JOINED = "JOINED"
    READY = "READY"
    CHECKED_IN = "CHECKED_IN"
    CALLED = "CALLED"
    SERVICE_STARTED = "SERVICE_STARTED"
    SERVICE_COMPLETED = "SERVICE_COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class QueueEvent(Base):
    __tablename__ = "queue_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    queue_entry_id: Mapped[int] = mapped_column(
        ForeignKey("queue_entries.id"), index=True, nullable=False
    )
    event_type: Mapped[QueueEventType] = mapped_column(
        SqlEnum(QueueEventType, name="queue_event_type"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    queue_entry: Mapped["QueueEntry"] = relationship(back_populates="events")
