from typing import Optional
from sqlalchemy import BIGINT, DECIMAL, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin, TimestampMixin


class Payment(Base, TableNameMixin, TimestampMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=True, default="USD")
    payment_method: Mapped[str] = mapped_column(String)
    is_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    hash: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    subscription_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("subscriptions.id"), nullable=True)

    # Add relationship to Subscription
    subscription: Mapped[Optional["Subscription"]] = relationship("Subscription", back_populates="payments")
