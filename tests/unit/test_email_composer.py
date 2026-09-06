"""
Unit tests for Email Composer templates and structures.
"""

import unittest
from components.email_composer import PREBUILT_TEMPLATES

class TestEmailComposerTemplates(unittest.TestCase):

    def test_prebuilt_templates_present(self):
        self.assertGreaterEqual(len(PREBUILT_TEMPLATES), 8)
        for name, data in PREBUILT_TEMPLATES.items():
            self.assertIn("subject", data)
            self.assertIn("body", data)
            self.assertTrue(len(data["subject"]) > 5)
            self.assertTrue(len(data["body"]) > 20)

    def test_project_status_template(self):
        status_key = [k for k in PREBUILT_TEMPLATES.keys() if "Progress" in k or "Status" in k][0]
        self.assertIn("Milestones", PREBUILT_TEMPLATES[status_key]["body"])

    def test_btech_major_project_template(self):
        acad_key = [k for k in PREBUILT_TEMPLATES.keys() if "Academic" in k or "BTech" in k][0]
        self.assertIn("BTech Major Project", PREBUILT_TEMPLATES[acad_key]["subject"])
        self.assertIn("Hriday", PREBUILT_TEMPLATES[acad_key]["body"])

    def test_meeting_and_leave_templates(self):
        meet_key = [k for k in PREBUILT_TEMPLATES.keys() if "Meeting" in k][0]
        self.assertIn("Meeting Request", PREBUILT_TEMPLATES[meet_key]["subject"])

        leave_key = [k for k in PREBUILT_TEMPLATES.keys() if "Holiday" in k or "Leave" in k][0]
        self.assertIn("Leave Application", PREBUILT_TEMPLATES[leave_key]["subject"])
        self.assertIn("absence", PREBUILT_TEMPLATES[leave_key]["body"].lower())

if __name__ == "__main__":
    unittest.main()
