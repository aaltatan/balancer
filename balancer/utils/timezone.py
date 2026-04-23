from datetime import datetime, timezone

import pytz

from balancer.config import get_config


def get_tz_now(timezone_name: str) -> datetime:
    return datetime.now(timezone.utc).astimezone(pytz.timezone(timezone_name))


def get_default_tz_now() -> datetime:
    return get_tz_now(get_config().default_timezone)
