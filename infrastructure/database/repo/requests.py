from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.admin import AdminRepo
from infrastructure.database.repo.order import OrderRepo
from infrastructure.database.repo.plans import PlanRepo
from infrastructure.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def plans(self) -> PlanRepo:
        return PlanRepo(self.session)

    @property
    def orders(self) -> OrderRepo:
        return OrderRepo(self.session)

    @property
    def admins(self) -> AdminRepo:
        return AdminRepo(self.session)
