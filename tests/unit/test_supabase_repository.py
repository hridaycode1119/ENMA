"""
Unit tests for SupabaseManager and AIRARepository data access layer.
"""

import unittest
from database.supabase_client import SupabaseManager
from database.repository import AIRARepository

class TestSupabaseRepository(unittest.TestCase):

    def setUp(self):
        self.sb_mgr = SupabaseManager()
        self.repo = AIRARepository()

    def test_supabase_manager_singleton(self):
        m1 = SupabaseManager()
        m2 = SupabaseManager()
        self.assertIs(m1, m2)

    def test_repository_save_and_get_task(self):
        task_id = "test-task-123"
        saved = self.repo.save_task(
            task_id=task_id,
            user_instruction="Test instruction for Supabase integration",
            state="COMPLETED",
            tool_name="gmail_send_tool",
            execution_time_ms=120.0,
        )
        self.assertEqual(saved["id"], task_id)
        self.assertEqual(saved["state"], "COMPLETED")

        recent = self.repo.get_recent_tasks(limit=5)
        self.assertTrue(any(t["id"] == task_id for t in recent))

    def test_repository_task_metrics(self):
        metrics = self.repo.get_task_metrics()
        self.assertIn("total_tasks", metrics)
        self.assertIn("completed", metrics)
        self.assertIn("emails_sent", metrics)
        self.assertGreaterEqual(metrics["total_tasks"], 1)

    def test_repository_calendar_event(self):
        evt = self.repo.save_calendar_event(
            event_id="test-evt-999",
            title="Supabase Review Meeting",
            event_time="Tomorrow, 02:00 PM",
            duration="45 mins",
            meet_url="https://meet.google.com/test-meet-url",
            attendees=["hriday.code1119@gmail.com"],
        )
        self.assertEqual(evt["title"], "Supabase Review Meeting")

        events = self.repo.get_calendar_events()
        self.assertTrue(any(e["id"] == "test-evt-999" for e in events))

    def test_repository_notes_and_journals(self):
        self.repo.save_note(
            title="Test Engineering Note",
            content="Supabase database integration verified.",
            category="note",
        )
        notes = self.repo.get_notes(category="note")
        self.assertTrue(any(n["title"] == "Test Engineering Note" for n in notes))

    def test_repository_documents(self):
        doc = self.repo.save_document(
            doc_id="test-doc-01",
            filename="test_report.pdf",
            file_type="pdf",
            word_count=500,
            page_count=2,
            raw_text="Sample text content for test.",
        )
        self.assertEqual(doc["filename"], "test_report.pdf")
        recent_docs = self.repo.get_recent_documents(limit=5)
        self.assertTrue(any(d["id"] == "test-doc-01" for d in recent_docs))

if __name__ == "__main__":
    unittest.main()
