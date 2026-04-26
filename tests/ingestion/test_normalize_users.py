"""
test_normalize_users.py
─────────────────────────────────────────────
Unit tests on normalize_user() from users.py
─────────────────────────────────────────────
"""

import pytest
from datetime import timezone
from unittest.mock import patch

try:
    from ingestion.users import normalize_user
except ImportError:
    from users import normalize_user


class TestNormalizeUser:

    def test_normalize_user_valid(self, raw_user):
        """A complete user is normalized correctly."""
        result = normalize_user(raw_user)

        assert result["id"] == 1
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["email"] == "john.doe@example.com"
        assert result["phone"] == "+1-555-0100"
        assert result["age"] == 30
        assert result["city"] == "Paris"
        assert result["country"] == "France"
        assert result["company_name"] == "Acme Corp"
        assert result["ingested_at"].tzinfo == timezone.utc

    def test_normalize_user_missing_id_raises(self):
        """A user without id raises a ValueError."""
        with pytest.raises(ValueError, match="'id' missing"):
            normalize_user({"firstName": "John", "email": "john@example.com"})

    def test_normalize_user_missing_email_raises(self):
        """A user without email raises a ValueError."""
        with pytest.raises(ValueError, match="'email' missing"):
            normalize_user({"id": 1, "firstName": "John"})

    def test_normalize_user_missing_optionals_returns_none(self, raw_user_missing_optionals):
        """Missing optional fields return None without raising."""
        result = normalize_user(raw_user_missing_optionals)

        assert result["phone"] is None
        assert result["age"] is None
        assert result["city"] is None
        assert result["country"] is None
        assert result["company_name"] is None

    def test_normalize_user_missing_optionals_logs_warning(self, raw_user_missing_optionals):
        """Missing optional fields trigger a warning log."""
        with patch("ingestion.users.logger") as mock_logger:
            normalize_user(raw_user_missing_optionals)
            assert mock_logger.warning.called

    def test_normalize_user_returns_ingested_at(self, raw_user):
        """ingested_at is always present and timezone-aware."""
        result = normalize_user(raw_user)
        assert result["ingested_at"] is not None
        assert result["ingested_at"].tzinfo is not None