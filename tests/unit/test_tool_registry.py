"""
Unit tests for Dynamic Tool Registry and Action Guard safety checks.
"""

import unittest
from tools.base import ToolSafetyLevel
from tools.registry import ToolRegistry
from security.action_guard import ActionGuard
from schemas.task_schemas import EmailDraftPayload

class TestToolRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry()

    def test_default_tools_registered(self):
        tool_names = self.registry.list_tool_names()
        self.assertIn("gmail_send_tool", tool_names)
        self.assertIn("gmail_draft_tool", tool_names)

        send_tool = self.registry.get_tool("gmail_send_tool")
        self.assertIsNotNone(send_tool)
        self.assertEqual(send_tool.metadata.safety_level, ToolSafetyLevel.CONSEQUENTIAL)

        draft_tool = self.registry.get_tool("gmail_draft_tool")
        self.assertIsNotNone(draft_tool)
        self.assertEqual(draft_tool.metadata.safety_level, ToolSafetyLevel.WRITE_SAFE)

    def test_action_guard_blocks_unconfirmed_consequential_tool(self):
        params = {
            "recipient_email": "advisor@university.edu",
            "subject": "Phase 1 Complete",
            "body_text": "Phase 1 is complete.",
        }

        # Attempt execution without user confirmation
        result = self.registry.execute_tool("gmail_send_tool", params, user_confirmed=False)
        self.assertFalse(result.success)
        self.assertIn("requires explicit human confirmation", result.error_message)

    def test_action_guard_permits_write_safe_tool_without_confirmation(self):
        params = {
            "recipient_email": "advisor@university.edu",
            "subject": "Phase 1 Draft",
            "body_text": "Draft body text.",
        }

        # Write-safe draft tool does not require strict manual confirmation
        result = self.registry.execute_tool("gmail_draft_tool", params, user_confirmed=False)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.external_reference_id)
        self.assertGreaterEqual(result.execution_time_ms, 0.0)

    def test_action_guard_permits_confirmed_consequential_tool(self):
        params = {
            "recipient_email": "advisor@university.edu",
            "subject": "Phase 1 Complete",
            "body_text": "Phase 1 is complete.",
        }

        # Executing with user confirmation succeeds
        result = self.registry.execute_tool("gmail_send_tool", params, user_confirmed=True)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.external_reference_id)
        self.assertIn("18f9", result.external_reference_id)

    def test_unknown_tool_lookup(self):
        result = self.registry.execute_tool("non_existent_tool", {}, user_confirmed=True)
        self.assertFalse(result.success)
        self.assertIn("not registered", result.error_message)

if __name__ == "__main__":
    unittest.main()
