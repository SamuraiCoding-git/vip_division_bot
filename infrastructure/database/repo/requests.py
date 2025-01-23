from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.admin import AdminRepo
from infrastructure.database.repo.blacklist import BlacklistRepo
from infrastructure.database.repo.order import OrderRepo
from infrastructure.database.repo.payment import PaymentRepo
from infrastructure.database.repo.plans import PlanRepo
from infrastructure.database.repo.setting import SettingRepo
from infrastructure.database.repo.subscription import SubscriptionRepo
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

    @property
    def settings(self) -> SettingRepo:
        return SettingRepo(self.session)

    @property
    def blacklist(self) -> BlacklistRepo:
        return BlacklistRepo(self.session)

    @property
    def payments(self) -> PaymentRepo:
        return PaymentRepo(self.session)

    @property
    def subscriptions(self) -> SubscriptionRepo:
        return SubscriptionRepo(self.session)
