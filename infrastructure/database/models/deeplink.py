import secrets
from typing import Optional

from sqlalchemy import BIGINT, DateTime, String, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin
from tgbot.utils.deeplink_utils import base62_encode


class DeepLink(Base, TableNameMixin):
    id: Mapped[str] = mapped_column(String(16), primary_key=True, unique=True)
    raw_data: Mapped[str] = mapped_column(String(256))
    action: Mapped[str] = mapped_column(String(64))
    params: Mapped[dict] = mapped_column(JSON)
    user_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=True)
    is_activated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_id() -> str:
        random_number = secrets.randbits(64)  # Генерируем случайное 64-битное число
        return base62_encode(random_number)
