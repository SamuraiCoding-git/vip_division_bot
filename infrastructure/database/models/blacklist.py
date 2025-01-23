from sqlalchemy import ForeignKey, BIGINT
from sqlalchemy.orm import relationship, mapped_column, Mapped

from infrastructure.database.models import Base
from infrastructure.database.models.base import TimestampMixin, TableNameMixin


class Blacklist(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="blacklist_entry")
