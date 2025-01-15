from typing import Optional

from sqlalchemy import BIGINT, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin
from infrastructure.database.models.enums import SubscriptionStatus


class Subscription(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("plans.id"), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.PENDING)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_recurrent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_gifted: Mapped[bool] = mapped_column(Boolean, default=False)
    gifted_by: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions", foreign_keys="Subscription.user_id")
    plan: Mapped["Plan"] = relationship("Plan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="subscription")
    gifted_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys="Subscription.gifted_by")
