from typing import Optional

from sqlalchemy import BIGINT, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin


class Admin(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(128))
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
