FROM apache/airflow:2.11.2

USER root

RUN apt-get update && apt-get install -y docker.io

RUN groupmod -g 1001 docker || groupadd -g 1001 docker

RUN usermod -aG docker airflow

USER airflow