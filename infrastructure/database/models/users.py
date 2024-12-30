from typing import Optional

from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, TableNameMixin


class User(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    plan_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("plans.id"), nullable=True)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="users")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User {self.id} {self.username} {self.full_name} Plan: {self.plan_id}>"
