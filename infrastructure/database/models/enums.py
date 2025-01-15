from enum import Enum as PyEnum


class PaymentMethod(PyEnum):
    CARD_RU = "card_ru"
    CARD_FOREIGN = "card_foreign"
    CRYPTO = "crypto"


class SubscriptionStatus(PyEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"


class Source(PyEnum):
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    DIRECT = "direct"
    OTHER = "other"
