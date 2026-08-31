"""
Unit tests for DocumentEditor and AI transformation commands.
"""

import unittest
from modules.documents.editor import DocumentEditor

class TestDocumentEditor(unittest.TestCase):

    def setUp(self):
        self.editor = DocumentEditor()
        self.sample_text = (
            "# Project Specification\n"
            "The client company is Acme Corp.\n"
            "Acme Corp requires an automated email and document system.\n"
            "Delivery milestone is scheduled for Friday."
        )

    def test_search_and_replace_case_insensitive(self):
        edited, count = self.editor.search_and_replace(self.sample_text, "acme corp", "Beta Ltd", case_sensitive=False)
        self.assertEqual(count, 2)
        self.assertIn("Beta Ltd", edited)
        self.assertNotIn("Acme Corp", edited)

    def test_append_and_prepend_section(self):
        appended = self.editor.append_section(self.sample_text, "Conclusion", "All goals achieved.")
        self.assertIn("## Conclusion\nAll goals achieved.", appended)

        prepended = self.editor.prepend_section(self.sample_text, "Confidential Notice", "For internal use only.")
        self.assertTrue(prepended.startswith("## Confidential Notice\nFor internal use only."))

    def test_ai_summarization_command(self):
        summary, note = self.editor.execute_ai_command(self.sample_text, "Generate an executive summary")
        self.assertIn("Executive Summary", summary)
        self.assertIn("Core Takeaways", summary)

    def test_ai_action_items_command(self):
        checklist, note = self.editor.execute_ai_command(self.sample_text, "Extract action items checklist")
        self.assertIn("Action Items", checklist)
        self.assertIn("- [ ]", checklist)

if __name__ == "__main__":
    unittest.main()
