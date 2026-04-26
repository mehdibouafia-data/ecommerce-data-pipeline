"""
test_load.py
─────────────────────────────────────────────
Unit tests on load_bigquery.py
Mock psycopg2 and google-cloud-bigquery
─────────────────────────────────────────────
"""

from unittest.mock import MagicMock, patch


class TestFetchFromPostgres:

    def test_fetch_returns_rows_and_columns(self):
        """fetch_from_postgres returns the rows and columns."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchall.return_value = [
            {"cart_id": 1, "product_id": 1},
            {"cart_id": 1, "product_id": 2},
        ]
        mock_cursor.description = [
            MagicMock(spec=str),
            MagicMock(spec=str),
        ]
        mock_cursor.description[0].__getitem__ = lambda self, i: "cart_id"
        mock_cursor.description[1].__getitem__ = lambda self, i: "product_id"

        from load.load_bigquery import fetch_from_postgres
        rows, columns = fetch_from_postgres(mock_conn, "int_orders_enriched")

        assert len(rows) == 2
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM intermediate.int_orders_enriched"
        )

    def test_fetch_empty_table_returns_empty_list(self):
        """fetch_from_postgres returns an empty list if the table is empty."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = []

        from load.load_bigquery import fetch_from_postgres
        rows, columns = fetch_from_postgres(mock_conn, "int_orders_enriched")

        assert rows == []


class TestLoadToBigQuery:

    def test_load_calls_bigquery_with_correct_table_ref(self):
        """load_to_bigquery calls the BigQuery client with the correct table ref."""
        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_client.load_table_from_json.return_value = mock_job

        mock_config = MagicMock()
        mock_config.gcp_project_id = "my-project"
        mock_config.gcp_dataset_intermediate = "ecommerce_intermediate"

        rows = [{"cart_id": 1, "product_id": 1}]

        from load.load_bigquery import load_to_bigquery
        load_to_bigquery(mock_client, mock_config, "int_orders_enriched", rows)

        mock_client.load_table_from_json.assert_called_once()
        call_args = mock_client.load_table_from_json.call_args
        assert call_args[0][1] == "my-project.ecommerce_intermediate.int_orders_enriched"
        mock_job.result.assert_called_once()

    def test_load_uses_write_truncate(self):
        """load_to_bigquery uses WRITE_TRUNCATE to be idempotent."""
        from google.cloud import bigquery
        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_client.load_table_from_json.return_value = mock_job

        mock_config = MagicMock()
        mock_config.gcp_project_id = "my-project"
        mock_config.gcp_dataset_intermediate = "ecommerce_intermediate"

        from load.load_bigquery import load_to_bigquery
        load_to_bigquery(mock_client, mock_config, "int_orders_enriched", [{"id": 1}])

        job_config = mock_client.load_table_from_json.call_args[1]["job_config"]
        assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_TRUNCATE


class TestMainLoad:

    def test_main_skips_empty_tables(self):
        """main() ignore the empty tables with a warning."""
        with patch("load.load_bigquery.psycopg2.connect") as mock_pg, \
             patch("load.load_bigquery.bigquery.Client"), \
             patch("load.load_bigquery.fetch_from_postgres", return_value=([], [])), \
             patch("load.load_bigquery.logger") as mock_logger:

            mock_pg.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_pg.return_value.__exit__ = MagicMock(return_value=False)

            from load.load_bigquery import main
            main()

            assert mock_logger.warning.called

    def test_main_processes_all_tables(self):
        """main() processes all tables defined in TABLES."""
        rows = [{"cart_id": 1}]
        with patch("load.load_bigquery.psycopg2.connect") as mock_pg, \
             patch("load.load_bigquery.bigquery.Client"), \
             patch("load.load_bigquery.fetch_from_postgres", return_value=(rows, ["cart_id"])), \
             patch("load.load_bigquery.load_to_bigquery") as mock_load:

            mock_pg.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_pg.return_value.__exit__ = MagicMock(return_value=False)

            from load.load_bigquery import main, TABLES
            main()

            assert mock_load.call_count == len(TABLES)