from __future__ import annotations

import functools
import hashlib
import json
import logging
import pickle
from typing import Callable, ParamSpec, TypeVar

from django.core.cache import cache

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def redis_cached(ttl: int = 3_600) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to cache a function's return value in Redis for *ttl* seconds.
    If the wrapped function is called again with the *same positional and keyword
    arguments*, the cached value is returned instead of executing the function.

    Usage
    -----
    @redis_cached(ttl=86_400)  # 1 day
    def expensive_call(x: int, y: str) -> dict[str, Any]:
        ...
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        prefix = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key_data = (prefix, args, kwargs)
            try:
                key_bytes = pickle.dumps(key_data)
            except Exception:
                key_bytes = json.dumps(str(key_data)).encode()
            cache_key = f"redis_cached:{hashlib.md5(key_bytes).hexdigest()}"

            cached: T | None = cache.get(cache_key)
            if cached is not None:
                logger.debug("Redis hit → %s", cache_key)
                return cached

            result: T = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=ttl)
            logger.debug("Redis miss → %s (stored %ss)", cache_key, ttl)
            return result

        return wrapper

    return decorator
