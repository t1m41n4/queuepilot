from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.queue import Queue
    from app.models.queue_event import QueueEvent


class QueueEntryStatus(str, Enum):
    WAITING = "WAITING"
    READY = "READY"
    CHECKED_IN = "CHECKED_IN"
    SERVING = "SERVING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class QueueEntry(Base):
    __tablename__ = "queue_entries"
    __table_args__ = (
        UniqueConstraint("queue_id", "queue_number", name="uq_queue_entries_queue_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    queue_id: Mapped[int] = mapped_column(ForeignKey("queues.id"), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    queue_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[QueueEntryStatus] = mapped_column(
        SqlEnum(QueueEntryStatus, name="queue_entry_status"), nullable=False
    )
    estimated_wait_minutes: Mapped[int | None] = mapped_column(Integer)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    queue: Mapped["Queue"] = relationship(back_populates="entries")
    events: Mapped[list["QueueEvent"]] = relationship(back_populates="queue_entry")
