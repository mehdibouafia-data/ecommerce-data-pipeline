"""
users.py
─────────────────────────────────────────────
User ingestion from DummyJSON.

Deduplication strategy: ON CONFLICT DO NOTHING
→ a user is immutable (no updates expected)
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
def extract_users(config: Config) -> list[dict]:
    return extract_paginated(config.api_url_users, "users", config.limit_users)


# ── Normalization ─────────────────────────────────────────
def normalize_user(user: dict) -> dict:
    # Required fields — blocks the run if missing
    if not user.get("id"):
        raise ValueError(f"Invalid user — 'id' missing : {user}")
    if not user.get("email"):
        raise ValueError(f"User {user['id']} invalid — 'email' missing")
 
    # Optional fields — warning if missing, None in database
    for field in ("phone", "age"):
        if user.get(field) is None:
            logger.warning(f"User {user['id']} — '{field}' missing")
 
    if not user.get("address", {}).get("city"):
        logger.warning(f"User {user['id']} — 'address.city' missing")
    if not user.get("address", {}).get("country"):
        logger.warning(f"User {user['id']} — 'address.country' missing")
    if not user.get("company", {}).get("name"):
        logger.warning(f"User {user['id']} — 'company.name' missing")
 
    return {
        "id":           user["id"],
        "first_name":   user["firstName"],
        "last_name":    user["lastName"],
        "email":        user["email"],
        "phone":        user.get("phone"),
        "age":          user.get("age"),
        "city":         user.get("address", {}).get("city"),
        "country":      user.get("address", {}).get("country"),
        "company_name": user.get("company", {}).get("name"),
        "ingested_at":  datetime.now(timezone.utc),
    }
 
 
# ── Upsert ────────────────────────────────────────────────
def upsert_users(conn, users: list[dict]) -> None:
    sql = """
        INSERT INTO raw.users
            (id, first_name, last_name, email, phone, age,
             city, country, company_name, ingested_at)
        VALUES
            (%(id)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(age)s,
             %(city)s, %(country)s, %(company_name)s, %(ingested_at)s)
        ON CONFLICT (id) DO NOTHING
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, users, page_size=100)
    conn.commit()
    logger.info(f"users inserted : {len(users)} rows")
 
 
# ── Orchestration ─────────────────────────────────────────
def ingest_users(conn, config: Config) -> None:
    raw = extract_users(config)
    users = [normalize_user(u) for u in raw]
    upsert_users(conn, users)
