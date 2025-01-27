from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from typing import Optional, List

from infrastructure.database.models import DeepLink


class DeepLinkRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, deeplink_id: int) -> Optional[DeepLink]:
        """Retrieve a DeepLink by its ID."""
        try:
            result = await self.session.execute(
                select(DeepLink).where(DeepLink.id == deeplink_id)
            )
            return result.scalar_one()
        except NoResultFound:
            return None

    async def get_all(self) -> List[DeepLink]:
        """Retrieve all DeepLinks."""
        result = await self.session.execute(select(DeepLink))
        return result.scalars().all()

    async def create(self, raw_data: str, action: str, params: dict, user_id: Optional[int] = None) -> DeepLink:
        """Create a new DeepLink."""
        new_deeplink = DeepLink(
            raw_data=raw_data,
            action=action,
            params=params,
            user_id=user_id,
        )
        self.session.add(new_deeplink)
        await self.session.commit()
        await self.session.refresh(new_deeplink)
        return new_deeplink

    async def update_activation_status(self, deeplink_id: int, is_activated: bool) -> Optional[DeepLink]:
        """Update the activation status of a DeepLink."""
        deeplink = await self.get_by_id(deeplink_id)
        if deeplink:
            deeplink.is_activated = is_activated
            await self.session.commit()
            await self.session.refresh(deeplink)
            return deeplink
        return None

    async def delete(self, deeplink_id: int) -> bool:
        """Delete a DeepLink by its ID."""
        deeplink = await self.get_by_id(deeplink_id)
        if deeplink:
            await self.session.delete(deeplink)
            await self.session.commit()
            return True
        return False
