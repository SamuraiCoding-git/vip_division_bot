from typing import Optional

from sqlalchemy import BIGINT, DateTime, String, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin


class DeepLink(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    raw_data: Mapped[str] = mapped_column(String(256))
    action: Mapped[str] = mapped_column(String(64))
    params: Mapped[dict] = mapped_column(JSON)
    user_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=True)
    is_activated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
