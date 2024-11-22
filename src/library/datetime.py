from datetime import date, datetime, tzinfo
from typing import Optional, Union

from config import CFG_TIMEZONE


def now(tz: Optional[tzinfo] = None) -> datetime:
    if tz is None:
        tz = CFG_TIMEZONE
    return datetime.now(tz=tz)


def date_format(dt: Union[date, datetime], fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    return dt.strftime(fmt)
