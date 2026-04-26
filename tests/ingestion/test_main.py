"""
test_main.py
─────────────────────────────────────────────
Unit tests on the CLI dispatch of main.py
─────────────────────────────────────────────
"""

import pytest
from unittest.mock import patch, MagicMock


MOCK_INGESTORS = {
    "users": MagicMock(),
    "products": MagicMock(),
    "carts": MagicMock(),
}


class TestMainDispatch:

    def setup_method(self):
        """Reset mocks before each test."""
        for mock in MOCK_INGESTORS.values():
            mock.reset_mock()

    def test_main_dispatches_users(self):
        """main() calls ingest_users when argument is 'users'."""
        with patch("sys.argv", ["main.py", "users"]), \
             patch("ingestion.main.Config") as mock_config, \
             patch("ingestion.main.psycopg2.connect") as mock_connect, \
             patch.dict("ingestion.main.INGESTORS", MOCK_INGESTORS):

            mock_config.return_value.postgres_dsn = "postgresql://fake"
            mock_connect.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)

            from ingestion.main import main
            main()
            MOCK_INGESTORS["users"].assert_called_once()

    def test_main_dispatches_products(self):
        """main() calls ingest_products when argument is 'products'."""
        with patch("sys.argv", ["main.py", "products"]), \
             patch("ingestion.main.Config") as mock_config, \
             patch("ingestion.main.psycopg2.connect") as mock_connect, \
             patch.dict("ingestion.main.INGESTORS", MOCK_INGESTORS):

            mock_config.return_value.postgres_dsn = "postgresql://fake"
            mock_connect.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)

            from ingestion.main import main
            main()
            MOCK_INGESTORS["products"].assert_called_once()

    def test_main_dispatches_carts(self):
        """main() calls ingest_carts when argument is 'carts'."""
        with patch("sys.argv", ["main.py", "carts"]), \
             patch("ingestion.main.Config") as mock_config, \
             patch("ingestion.main.psycopg2.connect") as mock_connect, \
             patch.dict("ingestion.main.INGESTORS", MOCK_INGESTORS):

            mock_config.return_value.postgres_dsn = "postgresql://fake"
            mock_connect.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)

            from ingestion.main import main
            main()
            MOCK_INGESTORS["carts"].assert_called_once()

    def test_main_invalid_argument_exits(self):
        """main() exits with sys.exit(1) if the argument is invalid."""
        with patch("sys.argv", ["main.py", "invalid"]):
            from ingestion.main import main
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1

    def test_main_no_argument_exits(self):
        """main() exits with sys.exit(1) if no argument is provided."""
        with patch("sys.argv", ["main.py"]):
            from ingestion.main import main
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1