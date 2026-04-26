#!/bin/bash
set -e

echo "── Initialization PostgreSQL ──"

# ── User + base Airflow ───────────────────────────────────
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOF

CREATE USER $POSTGRES_AIRFLOW_USER WITH PASSWORD '$POSTGRES_AIRFLOW_PASSWORD';
CREATE DATABASE $POSTGRES_AIRFLOW_DB OWNER $POSTGRES_AIRFLOW_USER;

EOF

# ── User + base ecommerce ─────────────────────────────────
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOF

CREATE USER $POSTGRES_ECOMMERCE_USER WITH PASSWORD '$POSTGRES_ECOMMERCE_PASSWORD';
CREATE DATABASE $POSTGRES_ECOMMERCE_DB OWNER $POSTGRES_ECOMMERCE_USER;

EOF

# ── Schemas raw, staging, intermediate ───────────────────
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_ECOMMERCE_DB" <<EOF

CREATE SCHEMA IF NOT EXISTS raw AUTHORIZATION $POSTGRES_ECOMMERCE_USER;
CREATE SCHEMA IF NOT EXISTS staging AUTHORIZATION $POSTGRES_ECOMMERCE_USER;
CREATE SCHEMA IF NOT EXISTS intermediate AUTHORIZATION $POSTGRES_ECOMMERCE_USER;

EOF

# ── Tables raw ────────────────────────────────────────────
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_ECOMMERCE_USER" --dbname "$POSTGRES_ECOMMERCE_DB" <<EOF

CREATE TABLE IF NOT EXISTS raw.users (
    id                INTEGER PRIMARY KEY,
    first_name        VARCHAR(100),
    last_name         VARCHAR(100),
    email             VARCHAR(255) UNIQUE NOT NULL,
    phone             VARCHAR(50),
    age               INTEGER,
    city              VARCHAR(100),
    country           VARCHAR(100),
    company_name      VARCHAR(255),
    ingested_at       TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS raw.products (
    id                    INTEGER PRIMARY KEY,
    title                 VARCHAR(255) NOT NULL,
    price                 NUMERIC(10, 2) NOT NULL,
    category              VARCHAR(100) NOT NULL,
    stock                 INTEGER,
    brand                 VARCHAR(100),
    rating                NUMERIC(3, 2),
    discount_percentage   NUMERIC(5, 2),
    ingested_at           TIMESTAMP WITH TIME ZONE,
    UNIQUE (title, category)
);

CREATE TABLE IF NOT EXISTS raw.carts (
    id                INTEGER PRIMARY KEY,
    user_id           INTEGER NOT NULL,
    total             NUMERIC(10, 2),
    discounted_total  NUMERIC(10, 2),
    ingested_at       TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES raw.users(id)
);

CREATE TABLE IF NOT EXISTS raw.cart_items (
    cart_id               INTEGER NOT NULL,
    product_id            INTEGER NOT NULL,
    title                 VARCHAR(255),
    price                 NUMERIC(10, 2),
    quantity              INTEGER,
    total                 NUMERIC(10, 2),
    discount_percentage   NUMERIC(5, 2),
    discounted_total      NUMERIC(10, 2),
    ingested_at           TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (cart_id, product_id),    
    FOREIGN KEY (cart_id) REFERENCES raw.carts(id),
    FOREIGN KEY (product_id) REFERENCES raw.products(id)
);

EOF

echo "── Initialization completed ──"