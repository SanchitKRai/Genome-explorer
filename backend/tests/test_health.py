"""Phase 1 tests: Backend health endpoint, CORS configuration, and error envelope."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import AppError, create_app


class TestPhase1Backend(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_health_endpoint_returns_expected_contract(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["phase"], 2)
        self.assertIn("version", data)
        self.assertFalse(data["ai_configured"])
        self.assertEqual(
            data["configured_model"],
            os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free"),
        )
        self.assertEqual(data["max_sequence_length_bp"], 100_000)

    def test_openapi_docs_endpoint_works(self) -> None:
        docs_res = self.client.get("/docs")
        self.assertEqual(docs_res.status_code, 200)
        openapi_res = self.client.get("/openapi.json")
        self.assertEqual(openapi_res.status_code, 200)
        self.assertIn("/api/health", openapi_res.json()["paths"])

    def test_cors_allows_vite_dev_origin_only(self) -> None:
        allowed = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(
            allowed.headers.get("access-control-allow-origin"),
            "http://localhost:5173",
        )

        disallowed = self.client.options(
            "/api/health",
            headers={
                "Origin": "https://malicious.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertIsNone(disallowed.headers.get("access-control-allow-origin"))

    def test_consistent_error_envelope(self) -> None:
        @self.app.get("/api/test-error")
        async def trigger_error() -> None:
            raise AppError(
                code="INVALID_BASE",
                message="Invalid character 'X' at position 12. Only A, T, G, C, and N are allowed.",
                status_code=400,
            )

        res = self.client.get("/api/test-error")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json(),
            {
                "error": {
                    "code": "INVALID_BASE",
                    "message": "Invalid character 'X' at position 12. Only A, T, G, C, and N are allowed.",
                }
            },
        )

    def test_router_stubs_mounted(self) -> None:
        for endpoint in ("mutate", "orfs", "explain"):
            res = self.client.get(f"/api/{endpoint}/status")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "scaffolded_phase_1")


if __name__ == "__main__":
    unittest.main()
