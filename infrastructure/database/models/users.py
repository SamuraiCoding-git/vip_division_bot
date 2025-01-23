from typing import Optional

from sqlalchemy import BIGINT, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, class_mapper

from infrastructure.database.models import Base
from infrastructure.database.models.base import TimestampMixin, TableNameMixin


class User(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    plan_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("plans.id"), nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="user", foreign_keys="Subscription.user_id")
    deep_links: Mapped[list["DeepLink"]] = relationship("DeepLink")
    admin: Mapped["Admin"] = relationship("Admin", back_populates="user", uselist=False)
    blacklist_entry = relationship("Blacklist", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}
