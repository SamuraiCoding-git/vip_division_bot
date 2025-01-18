from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.models import Base
from infrastructure.database.models.base import TableNameMixin, TimestampMixin


class Admin(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id'), primary_key=True, autoincrement=False)
    user: Mapped["User"] = relationship("User", back_populates="admin")
