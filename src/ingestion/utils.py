# utils.py
import requests


def extract_paginated(url: str, root_key: str, limit: int) -> list[dict]:
    items, skip = [], 0
    page_size = min(limit, 100)

    while len(items) < limit:
        response = requests.get(
            url,
            params={"limit": page_size, "skip": skip},
            timeout=10
        )
        response.raise_for_status()
        batch = response.json()
        page = batch.get(root_key, [])

        if not page:
            break

        items.extend(page)
        skip += len(page)

        if skip >= batch.get("total", limit):
            break

    return items[:limit]