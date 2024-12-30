from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import ForeignKey, BIGINT, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.models.base import TableNameMixin, TimestampMixin, Base


class Order(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("plans.id"), nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    plan: Mapped["Plan"] = relationship("Plan")

    def get_days_remaining(self) -> Optional[int]:
        """
        Calculates the number of days remaining in the subscription.
        :return: Remaining days, or None if no valid plan is associated.
        """
        if self.plan:
            duration_days = self.plan.get_duration_in_days()
            end_date = self.start_date + timedelta(days=duration_days)
            remaining = (end_date - datetime.utcnow()).days
            return max(remaining, 0)
        return None

    def __repr__(self):
        return (
            f"<Order {self.id} User: {self.user_id} Plan: {self.plan_id} Total: {self.total_price} Status: {self.status}>"
        )
