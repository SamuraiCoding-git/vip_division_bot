from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

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
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)

    @property
    def plans(self) -> PlanRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return PlanRepo(self.session)

    @property
    def orders(self) -> OrderRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return OrderRepo(self.session)