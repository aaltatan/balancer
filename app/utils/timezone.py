from datetime import datetime, timezone
from functools import partial

import pytz

from app.core.config import get_config


def get_tz_now(timezone_name: str) -> datetime:
    return datetime.now(timezone.utc).astimezone(pytz.timezone(timezone_name))


get_default_tz_now = partial(get_tz_now, get_config().default_timezone)
