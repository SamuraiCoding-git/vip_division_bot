import locale
from datetime import datetime, timedelta


def get_readable_subscription_end_date(days_to_add: int) -> str:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    subscription_end_date = datetime.now() + timedelta(days=days_to_add)
    return subscription_end_date.strftime("%d %B %Y").capitalize()