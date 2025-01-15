from sqlalchemy import BIGINT, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin


class Settings(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    is_payment_active: Mapped[bool] = mapped_column(Boolean, default=True)
