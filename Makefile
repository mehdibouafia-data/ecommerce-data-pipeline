# ─────────────────────────────────────────────
# Extract AIRFLOW_UID from .env
# ─────────────────────────────────────────────
AIRFLOW_UID := $(shell grep AIRFLOW_UID .env | cut -d= -f2)

.PHONY: help setup venv build up down run test lint dbt-compile ci clean reset

# ─────────────────────────────────────────────
# HELP
# ─────────────────────────────────────────────
help:
	@echo ""
	@echo "  E-Commerce Data Pipeline — available commands"
	@echo ""
	@echo "  Setup"
	@echo "    make setup          Copy .env.example to .env"
	@echo "    make venv           Create virtualenv and install dev dependencies"
	@echo ""
	@echo "  Docker"
	@echo "    make build          Build all Docker images"
	@echo "    make up             Start Airflow + PostgreSQL"
	@echo "    make down           Stop all containers"
	@echo "    make reset          Stop containers and delete all volumes and logs"
	@echo ""
	@echo "  Pipeline"
	@echo "    make run            Trigger the ecommerce_pipeline DAG"
	@echo ""
	@echo "  Quality"
	@echo "    make test           Run pytest unit tests"
	@echo "    make lint           Run ruff linter"
	@echo "    make dbt-compile    Compile dbt models (syntax check)"
	@echo "    make ci             Run all quality checks (lint + test + dbt-compile)"
	@echo ""
	@echo "  Cleanup"
	@echo "    make clean          Remove containers and built images"
	@echo ""

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env created — fill in your values before running make up"; \
	else \
		echo "⚠️  .env already exists — skipping"; \
	fi

venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements-dev.txt
	@echo "✅ Virtualenv ready — run: source .venv/bin/activate"

# ─────────────────────────────────────────────
# DOCKER
# ─────────────────────────────────────────────
build:
	docker-compose build
	docker-compose --profile tools build
	
up:
	mkdir -p airflow/logs airflow/plugins

	# Logs → Airflow écrit (UID depuis .env), toi peux lire
	sudo chown -R $(AIRFLOW_UID):$(shell id -g) airflow/logs
	sudo chmod -R 750 airflow/logs

	# Code → reste à ton user
	chmod -R 755 airflow/dags airflow/plugins

	docker-compose up -d
	@echo "✅ Airflow UI available at http://localhost:8080 (admin / admin)"
	@echo "ℹ️  DAGs/plugins editable locally (owned by host user)"
	@echo "ℹ️  Logs writable by Airflow (UID $(AIRFLOW_UID)) and readable by your user"

down:
	docker-compose down

reset:
	@echo "⚠️  This will delete all PostgreSQL data, volumes, logs and dbt artifacts"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	sudo rm -rf airflow/logs/*
	sudo rm -rf dbt/ecommerce/logs/*
	sudo rm -rf dbt/ecommerce/target/*
	sudo rm -rf dbt/ecommerce/dbt_packages/*
	sudo rm -rf dbt/ecommerce/docs/*
	@echo "✅ Reset complete — BigQuery datasets are not affected"

clean:
	docker-compose down --rmi local
	@echo "✅ Removes containers and locally built images — official images kept"

clean-all:
	docker-compose down --rmi local
	docker rmi apache/airflow:2.11.2 postgres:15 2>/dev/null || true
	@echo "✅ All project images removed"
	
# ─────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────
run:
	docker exec airflow_scheduler airflow dags trigger ecommerce_pipeline
	@echo "✅ DAG triggered — monitor at http://localhost:8080"

# ─────────────────────────────────────────────
# QUALITY
# ─────────────────────────────────────────────
test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check src/ tests/

dbt-compile:
	.venv/bin/dbt compile \
		--project-dir dbt/ecommerce \
		--profiles-dir dbt/ecommerce \
		--target ci

ci: lint test dbt-compile
	@echo "✅ All checks passed"