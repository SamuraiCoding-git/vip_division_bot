from sqlalchemy import BIGINT, Float
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, TableNameMixin


class Plan(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256))
    original_price: Mapped[float] = mapped_column(Float, nullable=False)
    discounted_price: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[str] = mapped_column(String(64))

    users: Mapped[list["User"]] = relationship("User", back_populates="plan")

    def __repr__(self):
        return (
            f"<Plan {self.id} {self.name} {self.original_price} {self.discounted_price} {self.duration}>"
        )
