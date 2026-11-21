"""
Unit tests for ENMA Enterprise Ticket & Helpdesk Module.
Tests repository methods and FastAPI REST endpoints across issue categories:
- Workflow & operational bottlenecks
- Salary & compensation
- Holiday & leave coordination
- IT infrastructure & hardware
"""

import unittest
from fastapi.testclient import TestClient
from database.repository import ENMARepository
from api.index import app


class TestTicketsModule(unittest.TestCase):

    def setUp(self):
        self.repo = ENMARepository()
        self.client = TestClient(app)

    def test_initial_tickets_loaded(self):
        """Verify baseline starter tickets are present."""
        tickets = self.repo.get_tickets()
        self.assertGreaterEqual(len(tickets), 4)
        stats = self.repo.get_ticket_stats()
        self.assertIn("total", stats)
        self.assertIn("open", stats)
        self.assertIn("in_progress", stats)
        self.assertIn("resolved", stats)
        self.assertIn("urgent", stats)
        self.assertEqual(stats["total"], len(self.repo._local_tickets))

    def test_create_workflow_ticket(self):
        """Test creating a workflow bottleneck ticket."""
        ticket = self.repo.create_ticket(
            title="CI/CD Pipeline Runner Failure on Main Branch",
            category="Workflow / Operational Bottleneck",
            description="GitHub actions worker runs out of disk space during docker build step.",
            created_by_name="Hriday Khosla",
            created_by_email="hriday.khosla@enterprise.com",
            department="DevOps & Platform",
            priority="Urgent",
        )
        self.assertTrue(ticket["id"].startswith("tkt-"))
        self.assertEqual(ticket["title"], "CI/CD Pipeline Runner Failure on Main Branch")
        self.assertEqual(ticket["category"], "Workflow / Operational Bottleneck")
        self.assertEqual(ticket["priority"], "Urgent")
        self.assertEqual(ticket["status"], "Open")

    def test_create_salary_ticket(self):
        """Test creating a salary or payroll query ticket."""
        ticket = self.repo.create_ticket(
            title="TDS Deduction Discrepancy on August Pay Slip",
            category="Salary / Compensation / Payroll",
            description="Form 16 calculation has higher deduction than expected per new tax regime.",
            created_by_name="Pooja Sharma",
            created_by_email="pooja.sharma@enterprise.com",
            department="Finance",
            priority="High",
        )
        self.assertEqual(ticket["category"], "Salary / Compensation / Payroll")
        self.assertEqual(ticket["created_by_name"], "Pooja Sharma")

    def test_create_holiday_leave_ticket(self):
        """Test creating a holiday or leave coordination ticket."""
        ticket = self.repo.create_ticket(
            title="Annual Paid Leave Approval for Diwali Festival",
            category="Holiday / Leave Request",
            description="Requesting leave from Nov 1 to Nov 5 for festival travel with team coverage planned.",
            created_by_name="Rahul Verma",
            created_by_email="rahul.verma@enterprise.com",
            department="Engineering",
            priority="Medium",
        )
        self.assertEqual(ticket["category"], "Holiday / Leave Request")
        self.assertEqual(ticket["status"], "Open")

    def test_filter_tickets_by_category_and_status(self):
        """Test repository filtering by category, status, and search query."""
        salary_tickets = self.repo.get_tickets(category="Salary / Compensation / Payroll")
        for t in salary_tickets:
            self.assertEqual(t["category"], "Salary / Compensation / Payroll")

        open_tickets = self.repo.get_tickets(status="Open")
        for t in open_tickets:
            self.assertEqual(t["status"], "Open")

        searched = self.repo.get_tickets(search_query="payroll")
        self.assertTrue(len(searched) >= 1)

    def test_update_ticket_status(self):
        """Test transitioning ticket lifecycle states with resolution notes."""
        ticket = self.repo.create_ticket(
            title="Temporary Access Token Expired for Staging DB",
            category="Security & Access Permissions",
            description="Staging DB token renewal needed for automation testing.",
            created_by_name="Karan Mehta",
            created_by_email="karan.mehta@enterprise.com",
            department="QA Engineering",
            priority="High",
        )
        tkt_id = ticket["id"]

        # Transition to In Progress
        updated = self.repo.update_ticket_status(tkt_id, "In Progress", "Infra team investigating token scope.")
        self.assertIsNotNone(updated)
        self.assertEqual(updated["status"], "In Progress")
        self.assertEqual(updated["resolution_note"], "Infra team investigating token scope.")

        # Transition to Resolved
        resolved = self.repo.update_ticket_status(tkt_id, "Resolved", "New 90-day credentials generated and mailed.")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["status"], "Resolved")

    def test_get_ticket_by_id_not_found(self):
        """Verify non-existent ticket returns None."""
        self.assertIsNone(self.repo.get_ticket_by_id("non-existent-id-999"))

    # --------------------------------------------------------------------------
    # REST API Endpoints Testing
    # --------------------------------------------------------------------------
    def test_api_get_tickets(self):
        """Test GET /api/tickets returns list of tickets and summary stats."""
        res = self.client.get("/api/tickets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tickets", data)
        self.assertIn("stats", data)
        self.assertIsInstance(data["tickets"], list)

    def test_api_create_and_fetch_ticket(self):
        """Test POST /api/tickets and GET /api/tickets/{ticket_id}."""
        payload = {
            "title": "Dual Monitor HDMI Cable Replacement Needed",
            "category": "IT & Infrastructure / Hardware",
            "description": "Desk #14 HDMI cable flickering during standup meetings.",
            "created_by_name": "Simran Patel",
            "created_by_email": "simran.patel@enterprise.com",
            "department": "Design",
            "priority": "Low",
        }
        post_res = self.client.post("/api/tickets", json=payload)
        self.assertEqual(post_res.status_code, 200)
        created = post_res.json()
        self.assertIn("id", created)
        t_id = created["id"]

        get_res = self.client.get(f"/api/tickets/{t_id}")
        self.assertEqual(get_res.status_code, 200)
        fetched = get_res.json()
        self.assertEqual(fetched["id"], t_id)
        self.assertEqual(fetched["title"], payload["title"])

    def test_api_patch_ticket(self):
        """Test PATCH /api/tickets/{ticket_id} status update."""
        payload = {
            "title": "API Rate Limit Adjustment for Partner Integration",
            "category": "Workflow / Operational Bottleneck",
            "description": "Need quota increased from 500 req/min to 2000 req/min for bulk sync.",
            "created_by_name": "Arjun Rao",
            "created_by_email": "arjun.rao@enterprise.com",
            "department": "Engineering",
            "priority": "High",
        }
        create_res = self.client.post("/api/tickets", json=payload)
        t_id = create_res.json()["id"]

        patch_res = self.client.patch(
            f"/api/tickets/{t_id}",
            json={"status": "Resolved", "resolution_note": "Rate limit doubled in API gateway config."},
        )
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["status"], "Resolved")

    def test_api_ticket_not_found(self):
        """Test 404 responses for missing tickets."""
        get_res = self.client.get("/api/tickets/tkt-invalid-999")
        self.assertEqual(get_res.status_code, 404)

        patch_res = self.client.patch(
            "/api/tickets/tkt-invalid-999",
            json={"status": "Closed"},
        )
        self.assertEqual(patch_res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
