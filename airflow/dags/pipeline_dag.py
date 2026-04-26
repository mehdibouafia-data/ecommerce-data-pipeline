"""
ecommerce_pipeline.py
─────────────────────────────────────────────────────────────
Main DAG for the e-commerce pipeline.

Flow :
  ingestion (users / products / carts in parallel)
    → dbt staging       → test staging
    → dbt intermediate  → test intermediate
    → load intermediate (PostgreSQL → BigQuery)
    → dbt marts         → test marts        (--target bigquery)
    → dbt docs generate
─────────────────────────────────────────────────────────────
"""

import os
from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.email import send_email
from docker.types import Mount

# ─────────────────────────────────────────────
# CONSTANTS 
# ─────────────────────────────────────────────
NETWORK       = "ecommerce-data-pipeline_default"
INGESTION_IMG = "ecommerce_ingestion:latest"
DBT_IMG       = "ecommerce_dbt:latest"
LOAD_IMG      = "ecommerce_load:latest"


# Bind mount dbt — persists models, logs, target, docs on the host
DBT_MOUNT = Mount(
    source=f"{os.getenv('PROJECT_PATH')}/dbt/ecommerce",
    target="/dbt/ecommerce",
    type="bind"
)

# LOAD Bind mount gcloud ADC — credentials BigQuery
LOAD_GCP_MOUNT = Mount(
    source=os.getenv('GCP_ADC_PATH'),
    target="/root/.config/gcloud",
    type="bind",
    read_only=True
)

# DBT Bind mount gcloud ADC — credentials BigQuery
DBT_GCP_MOUNT = Mount(
    source=os.getenv('GCP_ADC_PATH'),
    target="/home/dbtuser/.config/gcloud",
    type="bind",
    read_only=True
)

# Environment variables common to all tasks (ingestion + dbt + load)
COMMON_ENV = {
    "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
    "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
    "POSTGRES_ECOMMERCE_USER": os.getenv("POSTGRES_ECOMMERCE_USER"),
    "POSTGRES_ECOMMERCE_PASSWORD": os.getenv("POSTGRES_ECOMMERCE_PASSWORD"),
    "POSTGRES_ECOMMERCE_DB": os.getenv("POSTGRES_ECOMMERCE_DB"),
    "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID"),
    "GCP_DATASET_INTERMEDIATE": os.getenv("GCP_DATASET_INTERMEDIATE"),
    "GCP_DATASET_MARTS": os.getenv("GCP_DATASET_MARTS"),
    "GCP_LOCATION": os.getenv("GCP_LOCATION"),
}

# Environment variables specific to ingestion (row limits)
INGESTION_ENV = {
    **COMMON_ENV,
    "LIMIT_USERS": os.getenv("LIMIT_USERS"),
    "LIMIT_PRODUCTS": os.getenv("LIMIT_PRODUCTS"),
    "LIMIT_CARTS": os.getenv("LIMIT_CARTS"),
}

# ─────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────
def on_failure_alert(context):
    send_email(
        to=os.getenv("AIRFLOW_ADMIN_EMAIL"),
        subject=f"[FAILED] {context['task_instance'].task_id}",
        html_content=f"""
            <b>DAG</b>: {context['dag'].dag_id}<br>
            <b>Task</b>: {context['task_instance'].task_id}<br>
            <b>Error</b>: {context['exception']}
        """
    )

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def ingestion_task(task_id: str, entity: str, dag: DAG) -> DockerOperator:
    """Ingestion task — no GCP, no dbt mount."""
    return DockerOperator(
        task_id=task_id,
        image=INGESTION_IMG,
        command=f"python main.py {entity}",
        network_mode=NETWORK,
        auto_remove="success",
        environment= INGESTION_ENV,
        dag=dag,
    )


def dbt_task(task_id: str, command: str, dag: DAG, gcp: bool = False) -> DockerOperator:
    """
    Task dbt.
    gcp=True  → adds the GCP_MOUNT (required for --target bigquery)
    gcp=False → PostgreSQL only
    """
    mounts = [DBT_MOUNT]
    if gcp:
        mounts.append(DBT_GCP_MOUNT)

    return DockerOperator(
        task_id=task_id,
        image=DBT_IMG,
        command=command,
        network_mode=NETWORK,
        mounts=mounts,
        auto_remove="success",
        environment=COMMON_ENV,
        dag=dag,
    )


def load_task(task_id: str, dag: DAG) -> DockerOperator:
    """Task of transferring intermediate PostgreSQL → BigQuery."""
    return DockerOperator(
        task_id=task_id,
        image=LOAD_IMG,
        command="python load_bigquery.py",
        network_mode=NETWORK,
        mounts=[LOAD_GCP_MOUNT],
        auto_remove="success",
        environment=COMMON_ENV,
        dag=dag,
    )


# ─────────────────────────────────────────────
# DAG
# ─────────────────────────────────────────────
with DAG(
    dag_id="ecommerce_pipeline",
    description="Pipeline e-commerce : ingestion → dbt → BigQuery",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,   # oneshot — déclenché manuellement
    catchup=False,
    tags=["ecommerce", "ingestion", "dbt", "bigquery"],
    default_args={
        "on_failure_callback": on_failure_alert
    }
) as dag:

    # ── Parallel ingestion ───────────────────
    ingest_users    = ingestion_task("ingest_users",    "users",    dag)
    ingest_products = ingestion_task("ingest_products", "products", dag)
    ingest_carts    = ingestion_task("ingest_carts",    "carts",    dag)

    # ── dbt staging (PostgreSQL) ──────────────
    dbt_staging      = dbt_task("dbt_run_staging",  "dbt run  --select staging.*",  dag)
    dbt_test_staging = dbt_task("dbt_test_staging", "dbt test --select staging.*",  dag)

    # ── dbt intermediate (PostgreSQL) ─────────
    dbt_intermediate      = dbt_task("dbt_run_intermediate",  "dbt run  --select intermediate.*", dag)
    dbt_test_intermediate = dbt_task("dbt_test_intermediate", "dbt test --select intermediate.*", dag)

    # ── load intermediate → BigQuery ──────────
    load_intermediate = load_task("load_intermediate", dag)

    # ── dbt marts (BigQuery) ──────────────────
    dbt_marts      = dbt_task("dbt_run_marts",  "dbt run  --select marts.* --target bigquery", dag, gcp=True)
    dbt_test_marts = dbt_task("dbt_test_marts", "dbt test --select marts.* --target bigquery", dag, gcp=True)

    # ── dbt docs ──────────────────────────────
    dbt_docs = dbt_task("dbt_docs_generate", "dbt docs generate", dag, gcp=False)

    # ── Dépendances ───────────────────────────
    [ingest_users, ingest_products] >> ingest_carts
    ingest_carts          >> dbt_staging
    dbt_staging           >> dbt_test_staging
    dbt_test_staging      >> dbt_intermediate
    dbt_intermediate      >> dbt_test_intermediate
    dbt_test_intermediate >> load_intermediate
    load_intermediate     >> dbt_marts
    dbt_marts             >> dbt_test_marts
    dbt_test_marts        >> dbt_docs