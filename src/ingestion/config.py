"""
config.py
─────────────────────────────────────────────────────────────
Centralizes all container environment variables
ingestion. A single place to read the .env file — no more scattered
os.getenv() calls throughout the code.
─────────────────────────────────────────────────────────────
"""
 
import os
 
 
class Config:
 
    # ── API DummyJSON ──────────────────────────────────────
    api_url_users:    str = os.getenv("API_URL_USERS",    "https://dummyjson.com/users")
    api_url_products: str = os.getenv("API_URL_PRODUCTS", "https://dummyjson.com/products")
    api_url_carts:    str = os.getenv("API_URL_CARTS",    "https://dummyjson.com/carts")
 
    # ── Pagination limits (configurable via .env) ──────
    limit_users:    int = int(os.getenv("LIMIT_USERS",    "208"))
    limit_products: int = int(os.getenv("LIMIT_PRODUCTS", "194"))
    limit_carts:    int = int(os.getenv("LIMIT_CARTS",    "20"))
 
    # ── PostgreSQL DSN ─────────────────────────────────────
    # Built from the individual variables of the .env
    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://"
            f"{os.getenv('POSTGRES_ECOMMERCE_USER')}:"
            f"{os.getenv('POSTGRES_ECOMMERCE_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:"
            f"{os.getenv('POSTGRES_PORT')}/"
            f"{os.getenv('POSTGRES_ECOMMERCE_DB')}"
        )
 
