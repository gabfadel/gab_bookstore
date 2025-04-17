from __future__ import annotations

import logging
from typing import Any, Dict

import requests
from requests.exceptions import RequestException

from apps.core.cache_utils import redis_cached

logger = logging.getLogger(__name__)


@redis_cached(ttl=60 * 60 * 24 * 7)  # 7 days
def fetch_google_books_info(isbn: str) -> Dict[str, Any]:
    """
    Fetch book metadata from Google Books by ISBN.
    Cached in Redis for seven days to reduce external calls.
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}"}

    try:
        resp = requests.get(
            url,
            params=params,
            timeout=10,
            hooks={"response": lambda r, *_, **__: r.raise_for_status()},
        )
    except RequestException as exc:
        logger.warning("Google Books request error for %s → %s", isbn, exc)
        return {}

    data = resp.json()
    items = data.get("items")
    if not items:
        return {}

    volume = items[0].get("volumeInfo", {})
    enriched: Dict[str, Any] = {
        "title": volume.get("title"),
        "description": volume.get("description"),
        "published_date": volume.get("publishedDate"),
        "publisher": volume.get("publisher"),
        "page_count": volume.get("pageCount"),
    }

    if volume.get("authors"):
        enriched["author"] = ", ".join(volume["authors"])

    thumb = volume.get("imageLinks", {}).get("thumbnail")
    if thumb:
        enriched["cover_thumbnail"] = thumb

    return enriched
