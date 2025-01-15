from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from infrastructure.database.models import Base
from tgbot.config import DbConfig
from typing import Callable, AsyncContextManager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


async def create_session_pool(db: DbConfig, echo=False) -> Callable[[], AsyncContextManager[AsyncSession]]:
    engine = create_async_engine(
        db.construct_sqlalchemy_url(),
        query_cache_size=1200,
        pool_size=10,
        max_overflow=200,
        future=True,
        echo=echo,
    )

    async def create_tables():
        # Create an inspector object
        inspector = inspect(engine)

        # Check if the table exists
        if 'users' not in inspector.get_table_names():
            # Table doesn't exist, create all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        else:
            print("Table 'users' already exists. Skipping table creation.")

    session_pool = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    return session_pool
