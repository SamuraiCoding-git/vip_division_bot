from sqlalchemy import BIGINT, DECIMAL, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.models import Base
from infrastructure.database.models.base import TimestampMixin, TableNameMixin


class Plan(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256))
    original_price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    discounted_price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    duration: Mapped[int] = mapped_column(Integer)

    users: Mapped[list["User"]] = relationship("User", back_populates="plan")
