"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .user import user_router
from .media import media_router
from .navigation import navigation_router
from .subscription import subscription_router
from .payment import payment_router
from .start import start_router

routers_list = [
    admin_router,
    start_router,
    user_router,
    media_router,
    navigation_router,
    subscription_router,
    payment_router,
]

__all__ = [
    "routers_list",
]
