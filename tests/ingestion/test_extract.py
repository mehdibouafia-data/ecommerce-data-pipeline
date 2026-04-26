"""
test_extract.py
─────────────────────────────────────────────
Tests unitaires sur extract_paginated() de utils.py
Utilise requests_mock pour simuler l'API DummyJSON.
─────────────────────────────────────────────
"""

import pytest
import requests
import requests_mock as req_mock
from ingestion.utils import extract_paginated


BASE_URL = "https://dummyjson.com/users"


class TestExtractPaginated:

    def test_extract_paginated_single_page(self):
        """Retourne les items d'une seule page correctement."""
        with req_mock.Mocker() as m:
            m.get(BASE_URL, json={
                "users": [{"id": i} for i in range(1, 11)],
                "total": 10,
                "skip": 0,
                "limit": 10,
            })
            result = extract_paginated(BASE_URL, root_key="users", limit=10)
            assert len(result) == 10
            assert result[0]["id"] == 1

    def test_extract_paginated_respects_limit(self):
        """Ne retourne pas plus d'items que la limite demandée."""
        with req_mock.Mocker() as m:
            m.get(BASE_URL, json={
                "users": [{"id": i} for i in range(1, 101)],
                "total": 208,
                "skip": 0,
                "limit": 100,
            })
            result = extract_paginated(BASE_URL, root_key="users", limit=5)
            assert len(result) == 5

    def test_extract_paginated_empty_response(self):
        """Retourne une liste vide si l'API ne retourne rien."""
        with req_mock.Mocker() as m:
            m.get(BASE_URL, json={
                "users": [],
                "total": 0,
            })
            result = extract_paginated(BASE_URL, root_key="users", limit=10)
            assert result == []

    def test_extract_paginated_raises_on_http_error(self):
        """Lève une exception si l'API retourne une erreur HTTP."""
        with req_mock.Mocker() as m:
            m.get(BASE_URL, status_code=500)
            with pytest.raises(requests.exceptions.HTTPError):
                extract_paginated(BASE_URL, root_key="users", limit=10)

    def test_extract_paginated_raises_on_timeout(self):
        """Lève une exception en cas de timeout."""
        with req_mock.Mocker() as m:
            m.get(BASE_URL, exc=requests.exceptions.Timeout)
            with pytest.raises(requests.exceptions.Timeout):
                extract_paginated(BASE_URL, root_key="users", limit=10)