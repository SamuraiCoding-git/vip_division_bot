from typing import Optional

from sqlalchemy import BIGINT, Boolean, DateTime, ForeignKey, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin


class Subscription(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("plans.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_recurrent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_gifted: Mapped[bool] = mapped_column(Boolean, default=False)
    gifted_by: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False, default=None)

    # Correct the foreign_keys to use the actual column objects
    user: Mapped["User"] = relationship("User", back_populates="subscriptions", foreign_keys=[user_id])  # Use the column reference
    plan: Mapped["Plan"] = relationship("Plan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="subscription")
    gifted_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[gifted_by])  # Use the column reference specify the foreign key here
