"""
Integration tests for ResendSendTool registered in ToolRegistry.
"""

import unittest
from tools.registry import ToolRegistry
from tools.base import ToolSafetyLevel

class TestResendToolIntegration(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry()

    def test_resend_tool_registered(self):
        tool = self.registry.get_tool("resend_send_tool")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.metadata.safety_level, ToolSafetyLevel.CONSEQUENTIAL)

    def test_resend_tool_blocked_without_confirmation(self):
        result = self.registry.execute_tool(
            tool_name="resend_send_tool",
            parameters={
                "to": "chetan@enterprise.com",
                "subject": "Sprint Update",
                "body": "All deliverables are completed.",
            },
            user_confirmed=False,
        )
        self.assertFalse(result.success)
        self.assertIn("Action blocked", result.error_message)

    def test_resend_tool_executes_with_confirmation(self):
        result = self.registry.execute_tool(
            tool_name="resend_send_tool",
            parameters={
                "to": "chetan@enterprise.com",
                "subject": "Sprint Update",
                "body": "All deliverables are completed.",
            },
            user_confirmed=True,
        )
        self.assertTrue(result.success)
        self.assertIsNotNone(result.external_reference_id)
        self.assertEqual(result.data["status"], "sent")

if __name__ == "__main__":
    unittest.main()
