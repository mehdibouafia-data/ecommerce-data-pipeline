"""
test_normalize_products.py
─────────────────────────────────────────────
Unit tests on normalize_product() from products.py
─────────────────────────────────────────────
"""

import pytest
from datetime import timezone
from unittest.mock import patch

try:
    from ingestion.products import normalize_product
except ImportError:
    from products import normalize_product


class TestNormalizeProduct:

    def test_normalize_product_valid(self, raw_product):
        """A complete product is normalized correctly."""
        result = normalize_product(raw_product)

        assert result["id"] == 1
        assert result["title"] == "iPhone 15"
        assert result["price"] == 999.99
        assert result["category"] == "smartphones"
        assert result["stock"] == 50
        assert result["brand"] == "Apple"
        assert result["rating"] == 4.5
        assert result["discount_percentage"] == 10.0
        assert result["ingested_at"].tzinfo == timezone.utc

    def test_normalize_product_missing_id_raises(self):
        """A product without id raises a ValueError."""
        with pytest.raises(ValueError, match="'id' missing"):
            normalize_product({"title": "Phone", "price": 99.99, "category": "electronics"})

    def test_normalize_product_missing_title_raises(self):
        """A product without title raises a ValueError."""
        with pytest.raises(ValueError, match="'title' missing"):
            normalize_product({"id": 1, "price": 99.99, "category": "electronics"})

    def test_normalize_product_missing_price_raises(self):
        """A product without price raises a ValueError."""
        with pytest.raises(ValueError, match="'price' missing"):
            normalize_product({"id": 1, "title": "Phone", "category": "electronics"})

    def test_normalize_product_missing_category_raises(self):
        """A product without category raises a ValueError."""
        with pytest.raises(ValueError, match="'category' missing"):
            normalize_product({"id": 1, "title": "Phone", "price": 99.99})

    def test_normalize_product_missing_optionals_returns_none(self, raw_product_missing_optionals):
        """Missing optional fields return None without raising."""
        result = normalize_product(raw_product_missing_optionals)

        assert result["stock"] is None
        assert result["brand"] is None
        assert result["rating"] is None
        assert result["discount_percentage"] is None

    def test_normalize_product_missing_optionals_logs_warning(self, raw_product_missing_optionals):
        """Missing optional fields trigger a warning log."""
        with patch("ingestion.products.logger") as mock_logger:
            normalize_product(raw_product_missing_optionals)
            assert mock_logger.warning.called