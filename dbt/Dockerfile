FROM python:3.10-slim

# Create a user with the same UID as the host
ARG HOST_UID=1000
RUN useradd -m -u ${HOST_UID} dbtuser

WORKDIR /dbt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER dbtuser
WORKDIR /dbt/ecommerce