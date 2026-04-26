"""
load.py
─────────────────────────────────────────────────────────────
Transfers intermediate views from PostgreSQL to BigQuery.
Initiated by the Airflow DAG between dbt_test_intermediate and dbt_run_marts.

Flow:
    PostgreSQL intermediate.* → BigQuery ecommerce_intermediate.*
─────────────────────────────────────────────────────────────
"""

import logging
import psycopg2
import psycopg2.extras
from decimal import Decimal
from datetime import datetime, date
from google.cloud import bigquery

try:
    from config import Config          # Docker (WORKDIR /ingestion)
except ImportError:
    from load.config import Config  # pytest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Tables to transfer: PostgreSQL schema → BigQuery table
TABLES = [
    "int_orders_enriched",
    "int_customers_orders",
]

def serialize_row(row: dict) -> dict:
    """Converts non-JSON-serializable types to native Python types."""
    result = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, (datetime, date)):
            result[k] = v.isoformat()
        else:
            result[k] = v
    return result

def ensure_datasets(client: bigquery.Client, config: Config) -> None:
    """
    Creates the BigQuery datasets if they don't exist.
    Idempotent — exists_ok=True avoids any error in case of re-run.
    """
    for dataset_id in [config.gcp_dataset_intermediate, config.gcp_dataset_marts]:
        dataset = bigquery.Dataset(f"{config.gcp_project_id}.{dataset_id}")
        dataset.location = "EU"
        client.create_dataset(dataset, exists_ok=True)
        logger.info(f"BigQuery dataset ready : {dataset_id}")


def fetch_from_postgres(conn, table: str) -> tuple[list[dict], list[str]]:
    """
    Reads an intermediate view from PostgreSQL.
    Returns the rows and columns.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM intermediate.{table}")
        rows = [dict(row) for row in cur.fetchall()]
        columns = [desc[0] for desc in cur.description]
    logger.info(f"PostgreSQL → {table} : {len(rows)} rows fetched")
    return rows, columns


def load_to_bigquery(client: bigquery.Client, config: Config, table: str, rows: list[dict]) -> None:
    """
    Loads the rows into BigQuery.
    WRITE_TRUNCATE: replaces the table on each run — idempotent.
    """
    table_ref = f"{config.gcp_project_id}.{config.gcp_dataset_intermediate}.{table}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,    # Automatic pattern detection from the rows
    )

    rows = [serialize_row(row) for row in rows]
    job = client.load_table_from_json(rows, table_ref, job_config=job_config)
    job.result()  # wait until the job is finished

    logger.info(f"BigQuery → {table_ref} : {len(rows)} charged rows")


def main() -> None:
    config = Config()

    logger.info("Connection PostgreSQL...")
    pg_conn = psycopg2.connect(config.postgres_dsn)

    logger.info("Connection BigQuery...")
    bq_client = bigquery.Client(project=config.gcp_project_id)

    logger.info("Verification of BigQuery datasets...")
    ensure_datasets(bq_client, config)

    try:
        for table in TABLES:
            logger.info(f"── transfer {table} ──")
            rows, _ = fetch_from_postgres(pg_conn, table)

            if not rows:
                logger.warning(f"{table} vide — transfer ignored")
                continue

            load_to_bigquery(bq_client, config, table, rows)

    finally:
        pg_conn.close()

    logger.info("Transfer completed successfully.")

if __name__ == "__main__":
    main()