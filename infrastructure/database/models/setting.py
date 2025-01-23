from sqlalchemy import BIGINT, Boolean, Column, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin


class Setting(Base, TableNameMixin):
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    value: Mapped[bool] = mapped_column(Boolean, default=True)
    title: Mapped[str] = mapped_column(Text)
