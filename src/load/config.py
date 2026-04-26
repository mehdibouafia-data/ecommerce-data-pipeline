"""
config.py
─────────────────────────────────────────────────────────────
Container load environment variables.
─────────────────────────────────────────────────────────────
"""

import os


class Config:

    # ── PostgreSQL ─────────────────────────────────────────
    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://"
            f"{os.getenv('POSTGRES_ECOMMERCE_USER')}:"
            f"{os.getenv('POSTGRES_ECOMMERCE_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:"
            f"{os.getenv('POSTGRES_PORT')}/"
            f"{os.getenv('POSTGRES_ECOMMERCE_DB')}"
        )

    # ── BigQuery ───────────────────────────────────────────
    gcp_project_id:           str = os.getenv("GCP_PROJECT_ID")
    gcp_dataset_intermediate: str = os.getenv("GCP_DATASET_INTERMEDIATE")
    gcp_dataset_marts:        str = os.getenv("GCP_DATASET_MARTS")
    gcp_location:             str = os.getenv("GCP_LOCATION", "EU")  # default EU