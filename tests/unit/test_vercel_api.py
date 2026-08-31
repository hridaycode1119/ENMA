"""
Unit tests for Vercel Serverless FastAPI Endpoints (api/index.py).
"""

import unittest
from fastapi.testclient import TestClient
from api.index import app

class TestVercelServerlessAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("tools_count", data)

    def test_index_html_dashboard_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("AIRA - Autonomous AI Agent", response.text)

    def test_agent_command_endpoint(self):
        response = self.client.post(
            "/api/agent/command",
            json={"instruction": "Send email to chetan@enterprise.com with subject Project Update and body All milestones completed."},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("task_id", data)
        self.assertIn("task_type", data)
        self.assertEqual(data["state"], "AWAITING_APPROVAL")

    def test_tasks_and_metrics_endpoint(self):
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("metrics", data)
        self.assertIn("recent_tasks", data)

    def test_calendar_endpoints(self):
        get_res = self.client.get("/api/calendar")
        self.assertEqual(get_res.status_code, 200)

        post_res = self.client.post(
            "/api/calendar/schedule",
            json={"title": "Vercel Sprint Review", "event_time": "Tomorrow, 3 PM"},
        )
        self.assertEqual(post_res.status_code, 200)
        self.assertIn("meet_url", post_res.json())

    def test_document_edit_endpoint(self):
        response = self.client.post(
            "/api/documents/edit",
            json={"text": "Sample text for editing.", "instruction": "Summarize this document"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("edited_text", response.json())

if __name__ == "__main__":
    unittest.main()
