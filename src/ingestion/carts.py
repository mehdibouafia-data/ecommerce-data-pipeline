"""
carts.py
─────────────────────────────────────────────
Ingestion of orders from DummyJSON.
Flattens nested products into raw.cart_items.

Deduplication strategy: ON CONFLICT DO NOTHING
→ an order and its items are immutable
─────────────────────────────────────────────
"""

import logging
import psycopg2.extras
from datetime import datetime, timezone

try:
    from utils import extract_paginated          # Docker
except ImportError:
    from ingestion.utils import extract_paginated  # pytest

try:
    from config import Config          # Docker (WORKDIR /ingestion)
except ImportError:
    from ingestion.config import Config  # pytest

logger = logging.getLogger(__name__)


# ── Extraction ────────────────────────────────────────────
def extract_carts(config: Config) -> list[dict]:
    return extract_paginated(config.api_url_carts, "carts", config.limit_carts)


# ── Normalization ─────────────────────────────────────────
def normalize_cart(cart: dict) -> dict:
    # Required fields
    for field in ("id", "userId"):
        if not cart.get(field):
            raise ValueError(f"Invalid cart — '{field}' missing: {cart}")

    # Optional fields
    for field in ("total", "discountedTotal"):
        if cart.get(field) is None:
            logger.warning(f"Cart {cart['id']} — '{field}' missing")

    return {
        "id":               cart["id"],
        "user_id":          cart["userId"],
        "total":            cart.get("total"),
        "discounted_total": cart.get("discountedTotal"),
        "ingested_at":      datetime.now(timezone.utc),
    }


def normalize_cart_items(cart: dict) -> list[dict]:
    items = []
    for item in cart.get("products", []):
        # Required fields
        for field in ("id", "quantity"):
            if not item.get(field):
                raise ValueError(f"Invalid cart item — '{field}' missing in cart {cart['id']}: {item}")

        # Optional fields
        for field in ("title", "price", "total", "discountPercentage", "discountedTotal"):
            if item.get(field) is None:
                logger.warning(f"Cart {cart['id']} item {item.get('id')} — '{field}' missing")

        items.append({
            "cart_id":             cart["id"],
            "product_id":          item["id"],
            "title":               item.get("title"),
            "price":               item.get("price"),
            "quantity":            item.get("quantity"),
            "total":               item.get("total"),
            "discount_percentage": item.get("discountPercentage"),
            "discounted_total":    item.get("discountedTotal"),
            "ingested_at":         datetime.now(timezone.utc),
        })
    return items


# ── Upsert ────────────────────────────────────────────────
def upsert_carts(conn, carts: list[dict], cart_items: list[dict]) -> None:
    sql_carts = """
        INSERT INTO raw.carts
            (id, user_id, total, discounted_total, ingested_at)
        VALUES
            (%(id)s, %(user_id)s, %(total)s, %(discounted_total)s, %(ingested_at)s)
        ON CONFLICT (id) DO NOTHING
    """
    sql_items = """
        INSERT INTO raw.cart_items
            (cart_id, product_id, title, price, quantity,
             total, discount_percentage, discounted_total, ingested_at)
        VALUES
            (%(cart_id)s, %(product_id)s, %(title)s, %(price)s, %(quantity)s,
             %(total)s, %(discount_percentage)s, %(discounted_total)s, %(ingested_at)s)
        ON CONFLICT (cart_id, product_id) DO NOTHING
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql_carts, carts, page_size=100)
        psycopg2.extras.execute_batch(cur, sql_items, cart_items, page_size=100)
    conn.commit()
    logger.info(f"carts inserted: {len(carts)} rows | cart_items: {len(cart_items)} rows")


# ── Orchestration ─────────────────────────────────────────
def ingest_carts(conn, config: Config) -> None:
    raw = extract_carts(config)
    carts, cart_items = [], []
    for cart in raw:
        carts.append(normalize_cart(cart))
        cart_items.extend(normalize_cart_items(cart))
    upsert_carts(conn, carts, cart_items)