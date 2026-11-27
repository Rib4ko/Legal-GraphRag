"""
Unit test suite verifying FastAPI routing, schema validation, and health checks.
"""

import unittest
from fastapi.testclient import TestClient
import api


class TestLegalGraphRagAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(api.app)

    def test_health_check_endpoint(self):
        """Test the health check endpoint returns 200 and expected keys."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload.get("status"), "healthy")
        self.assertIn("neo4j_connected", payload)
        self.assertIn("llm_connected", payload)

    def test_translate_validation(self):
        """Test that translation endpoint validates non-empty payloads."""
        response = self.client.post("/api/translate", json={})
        self.assertEqual(response.status_code, 422)

    def test_search_validation(self):
        """Test that search endpoint requires valid query parameters."""
        response = self.client.post("/api/search", json={})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
