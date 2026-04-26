"""
conftest.py
─────────────────────────────────────────────
Fixtures shared between all tests.
─────────────────────────────────────────────
"""

import pytest


@pytest.fixture
def raw_user():
    return {
        "id": 1,
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0100",
        "age": 30,
        "address": {"city": "Paris", "country": "France"},
        "company": {"name": "Acme Corp"},
    }


@pytest.fixture
def raw_user_missing_optionals():
    """User valide mais sans champs optionnels."""
    return {
        "id": 2,
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane.smith@example.com",
        "phone": None,
        "age": None,
        "address": {},
        "company": {},
    }


@pytest.fixture
def raw_product():
    return {
        "id": 1,
        "title": "iPhone 15",
        "price": 999.99,
        "category": "smartphones",
        "stock": 50,
        "brand": "Apple",
        "rating": 4.5,
        "discountPercentage": 10.0,
    }


@pytest.fixture
def raw_product_missing_optionals():
    return {
        "id": 2,
        "title": "Generic Phone",
        "price": 199.99,
        "category": "smartphones",
        "stock": None,
        "brand": None,
        "rating": None,
        "discountPercentage": None,
    }


@pytest.fixture
def raw_cart():
    return {
        "id": 1,
        "userId": 1,
        "total": 150.00,
        "discountedTotal": 135.00,
        "products": [
            {
                "id": 1,
                "title": "iPhone 15",
                "price": 999.99,
                "quantity": 1,
                "total": 999.99,
                "discountPercentage": 10.0,
                "discountedTotal": 899.99,
            },
            {
                "id": 2,
                "title": "AirPods",
                "price": 199.99,
                "quantity": 2,
                "total": 399.98,
                "discountPercentage": 5.0,
                "discountedTotal": 379.98,
            },
        ],
    }


@pytest.fixture
def raw_cart_empty_products():
    return {
        "id": 2,
        "userId": 2,
        "total": 0.0,
        "discountedTotal": 0.0,
        "products": [],
    }