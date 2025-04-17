# apps/books/tests/mixins.py
from __future__ import annotations

from rest_framework.test import APITestCase, APIClient


class JWTAuthMixin(APITestCase):
    """
    Helper mix‑in that attaches a fresh JWT to ``self.client``

    Example
    -------
    token = self.authenticate_as(user)
    """

    RAW_PASSWORD: str = "admin123"

    def _jwt_for(self, user):
        tmp = APIClient()
        resp = tmp.post(
            "/v1/auth/login/",
            {"username": user.username, "password": self.RAW_PASSWORD},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        return resp.json()["access"]

    def authenticate_as(self, user):
        token = self._jwt_for(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token
