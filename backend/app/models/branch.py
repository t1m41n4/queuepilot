from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.bank import Bank
    from app.models.queue import Queue
    from app.models.staff import Staff


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bank_id: Mapped[int] = mapped_column(ForeignKey("banks.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    average_service_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    bank: Mapped["Bank"] = relationship(back_populates="branches")
    queue: Mapped["Queue"] = relationship(back_populates="branch", uselist=False)
    staff_members: Mapped[list["Staff"]] = relationship(back_populates="branch")
