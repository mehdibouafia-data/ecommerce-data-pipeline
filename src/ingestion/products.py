"""
products.py
─────────────────────────────────────────────
Product ingestion from DummyJSON.

Deduplication strategy: ON CONFLICT DO UPDATE
→ Price, stock, and rating may change between runs.
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
def extract_products(config: Config) -> list[dict]:
    return extract_paginated(config.api_url_products, "products", config.limit_products)


# ── Normalization ─────────────────────────────────────────
def normalize_product(product: dict) -> dict:
    # Required fields — blocks the run if missing
    for field in ("id", "title", "price", "category"):
        if not product.get(field):
            raise ValueError(f"Invalid product — '{field}' missing : {product}")
 
    # Optional fields — warning if missing, None in database
    for field in ("stock", "brand", "rating", "discountPercentage"):
        if product.get(field) is None:
            logger.warning(f"Product {product['id']} — '{field}' missing")
 
    return {
        "id":                  product["id"],
        "title":               product["title"],
        "price":               product["price"],
        "category":            product["category"],
        "stock":               product.get("stock"),
        "brand":               product.get("brand"),
        "rating":              product.get("rating"),
        "discount_percentage": product.get("discountPercentage"),
        "ingested_at":         datetime.now(timezone.utc),
    }
 
 
# ── Upsert ────────────────────────────────────────────────
def upsert_products(conn, products: list[dict]) -> None:
    sql = """
        INSERT INTO raw.products
            (id, title, price, category, stock, brand,
             rating, discount_percentage, ingested_at)
        VALUES
            (%(id)s, %(title)s, %(price)s, %(category)s, %(stock)s, %(brand)s,
             %(rating)s, %(discount_percentage)s, %(ingested_at)s)
        ON CONFLICT (id) DO UPDATE SET
            price               = EXCLUDED.price,
            stock               = EXCLUDED.stock,
            rating              = EXCLUDED.rating,
            discount_percentage = EXCLUDED.discount_percentage,
            ingested_at         = EXCLUDED.ingested_at
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, products, page_size=100)
    conn.commit()
    logger.info(f"products upserted : {len(products)} rows")
 
 
# ── Orchestration ─────────────────────────────────────────
def ingest_products(conn, config: Config) -> None:
    raw = extract_products(config)
    products = [normalize_product(p) for p in raw]
    upsert_products(conn, products)
