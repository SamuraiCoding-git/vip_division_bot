from typing import Optional

from sqlalchemy import BIGINT, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.models import Base
from infrastructure.database.models.base import TimestampMixin, TableNameMixin
from infrastructure.database.models.enums import Source


class User(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    plan_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("plans.id"), nullable=True)
    source: Mapped[Source] = mapped_column(Enum(Source), nullable=False, default=Source.DIRECT)
    # subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="user")
    # deep_links: Mapped[list["DeepLink"]] = relationship("DeepLink")

