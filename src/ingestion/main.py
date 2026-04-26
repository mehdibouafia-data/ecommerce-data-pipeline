"""
main.py
─────────────────────────────────────────────
Entry point for the ingestion container.
Receives a CLI argument to target the entity to ingest.

Usage:
    python main.py users
    python main.py products
    python main.py carts
─────────────────────────────────────────────
"""

import sys
import logging
import psycopg2


try:                                        # Docker (WORKDIR /ingestion)
    from users import ingest_users
    from products import ingest_products
    from carts import ingest_carts
    from config import Config
except ImportError:                         # pytest
    from ingestion.users import ingest_users
    from ingestion.products import ingest_products
    from ingestion.carts import ingest_carts
    from ingestion.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

INGESTORS = {
    "users":    ingest_users,
    "products": ingest_products,
    "carts":    ingest_carts,
}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in INGESTORS:
        logger.error(f"Usage : python main.py [{'|'.join(INGESTORS)}]")
        sys.exit(1)

    entity = sys.argv[1]
    config = Config()

    logger.info(f"Ingestion start → {entity}")

    with psycopg2.connect(config.postgres_dsn) as conn:
        INGESTORS[entity](conn, config)

    logger.info(f"Ingestion {entity} completed successfully.")


if __name__ == "__main__":
    main()