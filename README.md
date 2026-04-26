# 🛒 E-Commerce Data Pipeline

An e-commerce company generates thousands of orders daily. This pipeline ingests, transforms and delivers analytics-ready data — end-to-end, from a REST API to production-grade marts on BigQuery, ready for BI tools and ad-hoc analysis.

Built with a production-like architecture : layered data modeling (raw → staging → intermediate → marts), quality tested at every layer, orchestrated by Airflow, and validated with CI.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIRFLOW DAG                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌───────────────┐  ┌────────────┐             │
│  │ingest_users │  │ingest_products│  │ingest_carts│  parallel   │
│  └──────┬──────┘  └───────┬───────┘  └─────┬──────┘             │
│         └─────────────────┴────────────────┘                    │
│                            │                                    │
│                  ┌─────────▼──────────┐                         │
│                  │  PostgreSQL : raw  │                         │
│                  │ users, products,   │                         │
│                  │ carts, cart_items  │                         │
│                  └─────────┬──────────┘                         │   
│                            │                                    │
│                  ┌─────────▼──────────┐                         │
│                  │  dbt run staging   │                         │
│                  │  dbt test staging  │  PostgreSQL views       │
│                  └─────────┬──────────┘                         │
│                            │                                    │
│                  ┌─────────▼─────────────┐                       │
│                  │ dbt run intermediate  │                       │
│                  │ dbt test intermediate │ PostgreSQL views      │
│                  └─────────┬─────────────┘                       │ 
│                            │                                    │
│                  ┌─────────▼──────────┐                         │
│                  │     load.py        │                         │
│                  │ PostgreSQL → BQ    │  intermediate tables    │
│                  └─────────┬──────────┘                         │
│                            │                                    │
│                  ┌─────────▼──────────┐                         │
│                  │  dbt run marts     │                         │
│                  │  dbt test marts    │  BigQuery tables        │
│                  └─────────┬──────────┘                         │
│                            │                                    │
│                  ┌─────────▼──────────┐                         │
│                  │  dbt docs generate │                         │
│                  └─────────┬──────────┘                         │
└────────────────────────────┼────────────────────────────────────┘
                             │
                   ┌─────────▼──────────┐
                   │   Looker Studio    │
                   │    Dashboard       │
                   └────────────────────┘
```

---

## 🧰 Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | Apache Airflow 2.11.2 |
| Ingestion | Python, requests, psycopg2 |
| Storage (raw) | PostgreSQL 15 — tables |
| Storage (staging / intermediate) | PostgreSQL 15 — views |
| Storage (intermediate / marts) | Google BigQuery — tables |
| Transformation | dbt-core, dbt-postgres, dbt-bigquery |
| Containerisation | Docker, Docker Compose |
| Data Source | DummyJSON REST API |
| Visualisation | Looker Studio |
| CI | GitHub Actions |
| Linting | Ruff |
| Testing | Pytest, dbt tests, dbt compile |

---

## 📁 Project Structure

```
ecommerce-data-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml
├── airflow/
│   ├── Dockerfile                  # Custom scheduler — Docker CLI + GID
│   ├── dags/
│   │   └── ecommerce_pipeline.py   # Main DAG
│   ├── logs/
│   └── plugins/
├── docker/
│   ├── airflow-init.sh             # Airflow DB migration + admin user
│   └── init-db.sh                  # PostgreSQL users, databases, schemas
├── src/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py                 # CLI entrypoint (users / products / carts)
│   │   ├── config.py
│   │   ├── utils.py                # Paginated API extraction
│   │   ├── users.py
│   │   ├── products.py
│   │   └── carts.py

│   └── load/
│       ├── __init__.py
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── load_bigquery.py                 # PostgreSQL intermediate → BigQuery
│       └── config.py
├── dbt/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ecommerce/
│       ├── dbt_project.yml
│       ├── profiles.yml        # Two targets : PostgreSQL + BigQuery (ADC)
│       ├── models/
│       │   ├── staging/        # Views — PostgreSQL
│       │   ├── intermediate/   # Views — PostgreSQL
│       │   └── marts/          # Tables — BigQuery
│       ├── tests/              # Custom SQL assertions
        ├── macros/             # Macro pour générer le nom du schéma cible
│       └── analysis/           # Analytics queries (non-executed)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── test_normalize_users.py
│   │   ├── test_normalize_products.py
│   │   ├── test_normalize_carts.py
│   │   ├── test_extract.py
│   │   └── test_main.py
│   └── load/
│       ├── __init__.py
│       └── test_load.py
├── docker-compose.yml
├── pytest.ini
├── requirements-dev.txt
├── Makefile
├── .env.example
└── README.md
```

---

## 📊 Data Models

### Staging — PostgreSQL (views)

| Model | Source | Description |
|---|---|---|
| `stg_users` | `raw.users` | Cleaned and typed users |
| `stg_products` | `raw.products` | Cleaned and typed products |
| `stg_carts` | `raw.carts` | Cleaned and typed carts |
| `stg_cart_items` | `raw.cart_items` | Cleaned and typed cart items |

### Intermediate — PostgreSQL (views) → BigQuery (tables via load.py)

| Model | Description |
|---|---|
| `int_orders_enriched` | Cart items joined with carts and products |
| `int_customers_orders` | Users joined with their carts |

### Marts — BigQuery (tables)

| Model | Granularity | Key metrics |
|---|---|---|
| `mart_sales` | 1 row per cart item | Revenue, discount, % of cart, category rank, revenue quartile |
| `mart_customers` | 1 row per customer | LTV, order count, segment (high/mid/low), country rank |
| `mart_products` | 1 row per product | Revenue, units sold, performance score, low stock alert |

---

## ✅ Data Quality

**dbt generic tests** — `not_null`, `unique`, `accepted_values` declared in `schema.yml` at every layer.

**Custom SQL assertions** — 19 tests on business logic across staging, intermediate and marts.

---

## 🚀 How to Run

### Prerequisites

- Docker & Docker Compose
- `make`
- `gcloud` CLI ([install guide](https://cloud.google.com/sdk/docs/install))
- A GCP project with BigQuery enabled — datasets are created automatically on first run

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ecommerce-data-pipeline.git
cd ecommerce-data-pipeline
```

### 2. Configure environment variables

```bash
make setup
# Edit .env with your values
```

### 3. Authenticate with GCP

```bash
gcloud auth application-default login --no-launch-browser
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### 4. Build and start

```bash
make build
make up
```

Open [http://localhost:8080](http://localhost:8080) → `admin` / `admin`


### 5. Trigger the pipeline

In the Airflow UI, enable and manually trigger the `ecommerce_pipeline` DAG.

```bash
# Or via CLI
make run
```

Monitor the execution in the Airflow UI — tasks run in this order :

```
ingest_users   ─┐
ingest_products ┤ (parallel)
                └─→ ingest_carts → dbt staging → dbt test staging
                                 → dbt intermediate → dbt test intermediate
                                 → load intermediate (PostgreSQL → BigQuery)
                                 → dbt marts → dbt test marts
                                 → dbt docs generate
```

### 6. Browse dbt documentation

After a successful run, serve the dbt docs locally :

```bash
make venv
source ../../.venv/bin/activate
cd dbt/ecommerce
dbt docs serve --profiles-dir . --port 8081
```

Open [http://localhost:8081](http://localhost:8081) to explore the full data lineage, model descriptions and test results.


### 7. Reset everything

```bash
make reset    # stops containers, deletes pgdata (postgreSQL db) and all logs
make clean    # removes containers and locally built images (official images kept)

# make clean-all    # removes locally built images + official images (apache/airflow, postgres)
```

> ⚠️ BigQuery datasets are not affected by reset.

---

## 🧪 Running Tests Locally

```bash
make venv
source ../../.venv/bin/activate

make test           # 26 pytest unit tests
make lint           # ruff linter
make dbt-compile    # dbt SQL syntax check
make ci             # all checks at once
```

---

## 📈 Analytics Queries

Pre-built queries available in `src/dbt/ecommerce/analysis/` — run directly on BigQuery :

| Query | Description |
|---|---|
| `kpi_dashboard.sql` | Total revenue, orders, customers |
| `top_products_by_category.sql` | Top 3 products per category by revenue |
| `customer_segments_breakdown.sql` | Distribution of customer segments |
| `low_stock_products.sql` | Products with low stock alert by category |
| `product_recommendations.sql` | Top-rated products with strong sales performance |

---

## ⚙️ CI (Continuous Integration)

Triggers on every push to `main` or `develop` and on pull requests to `main`. Quality checks only — no deployment is automated as this project runs locally.

```
lint ──→ tests                    
     ├─→ dbt-compile               
     └─→ docker-compose-validate ──→ docker-build
```

| Job | What it checks |
|---|---|
| `lint` | Ruff on `src/` and `tests/` |
| `tests` | 26 pytest unit tests — no infrastructure required |
| `dbt-compile` | SQL syntax across all models |
| `docker-compose-validate` | docker-compose.yml syntax |
| `docker-build` | Build ingestion, dbt and load images |

---

## 🔒 Security

- No credentials committed — all secrets via `.env` (gitignored)
- GCP auth via **Application Default Credentials** — no service account JSON
- PostgreSQL least-privilege — separate users per database (`airflow` / `ecommerce`)
- Airflow logs restricted to owner and group (chmod 750) — not world-readable
- dbt container runs as non-root user (UID matching host) — prevents permission conflicts