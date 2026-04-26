"""
test_normalize_carts.py
─────────────────────────────────────────────
Unit tests on normalize_cart() and
normalize_cart_items() from carts.py
─────────────────────────────────────────────
"""

import pytest
from datetime import timezone

try:
    from ingestion.carts import normalize_cart, normalize_cart_items
except ImportError:
    from carts import normalize_cart, normalize_cart_items


class TestNormalizeCart:

    def test_normalize_cart_valid(self, raw_cart):
        """A complete cart is normalized correctly."""
        result = normalize_cart(raw_cart)

        assert result["id"] == 1
        assert result["user_id"] == 1
        assert result["total"] == 150.00
        assert result["discounted_total"] == 135.00
        assert result["ingested_at"].tzinfo == timezone.utc

    def test_normalize_cart_missing_id_raises(self):
        """A cart without id raises a ValueError."""
        with pytest.raises(ValueError, match="'id' missing"):
            normalize_cart({"userId": 1, "total": 100.0, "discountedTotal": 90.0, "products": []})

    def test_normalize_cart_missing_user_id_raises(self):
        """A cart without userId raises a ValueError."""
        with pytest.raises(ValueError, match="'userId' missing"):
            normalize_cart({"id": 1, "total": 100.0, "discountedTotal": 90.0, "products": []})


class TestNormalizeCartItems:

    def test_normalize_cart_items_valid(self, raw_cart):
        """Cart items are flattened correctly."""
        items = normalize_cart_items(raw_cart)

        assert len(items) == 2

        first = items[0]
        assert first["cart_id"] == 1
        assert first["product_id"] == 1
        assert first["title"] == "iPhone 15"
        assert first["price"] == 999.99
        assert first["quantity"] == 1
        assert first["total"] == 999.99
        assert first["discount_percentage"] == 10.0
        assert first["discounted_total"] == 899.99
        assert first["ingested_at"].tzinfo == timezone.utc

    def test_normalize_cart_items_empty_products(self, raw_cart_empty_products):
        """A cart with no products returns an empty list."""
        items = normalize_cart_items(raw_cart_empty_products)
        assert items == []

    def test_normalize_cart_items_missing_item_id_raises(self):
        """A cart item without id raises a ValueError."""
        cart = {
            "id": 1, "userId": 1, "total": 100.0, "discountedTotal": 90.0,
            "products": [{"quantity": 1, "price": 50.0}],
        }
        with pytest.raises(ValueError, match="'id' missing"):
            normalize_cart_items(cart)

    def test_normalize_cart_items_missing_quantity_raises(self):
        """A cart item without quantity raises a ValueError."""
        cart = {
            "id": 1, "userId": 1, "total": 100.0, "discountedTotal": 90.0,
            "products": [{"id": 1, "price": 50.0}],
        }
        with pytest.raises(ValueError, match="'quantity' missing"):
            normalize_cart_items(cart)

    def test_normalize_cart_items_count(self, raw_cart):
        """Item count matches the number of products in the cart."""
        items = normalize_cart_items(raw_cart)
        assert len(items) == len(raw_cart["products"])