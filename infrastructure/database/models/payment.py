from typing import Optional

from sqlalchemy import BIGINT, DECIMAL, Boolean, DateTime, ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin
from infrastructure.database.models.enums import PaymentMethod


class Payment(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)
    is_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    hash: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subscription_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("subscriptions.id"), nullable=True)
