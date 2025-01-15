from datetime import datetime

from sqlalchemy import ForeignKey, BIGINT, DateTime, Float, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.models.base import TableNameMixin, TimestampMixin, Base


class Order(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("plans.id"), nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hash: Mapped[str] = mapped_column(String, nullable=True)
    binding_id: Mapped[str] = mapped_column(String)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="plans")

    def __repr__(self):
        return (
            f"<Order {self.id} User: {self.user_id} Plan: {self.plan_id} Total: {self.total_price} Status: {self.is_paid}>"
        )
