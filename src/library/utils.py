from typing import Any, Dict, List, Union

import ujson
from config import logger


def json_loads(value: Union[bytes, str, None]) -> Union[List[Any], Dict[str, Any], None]:
    if value is None or not value:
        return None
    try:
        return ujson.loads(value)
    except (TypeError, ValueError):
        logger.error('JSON字符串解析失败: value={}', value)
        return None


def valid_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        i = int(value)
    except (TypeError, ValueError):
        i = default
        return i
    if i < minimum:
        i = minimum
    elif i > maximum:
        i = maximum
    else:
        pass
    return i


def valid_float(value: Any, default: float, minimum: float, maximum: float) -> float:
    try:
        i = float(value)
    except (TypeError, ValueError):
        i = default
        return i
    if i < minimum:
        i = minimum
    elif i > maximum:
        i = maximum
    else:
        pass
    return i
