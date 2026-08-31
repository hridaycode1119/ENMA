"""
Integration tests for End-to-End Task Parsing to Tool Dispatch.
"""

import os
import unittest
from agent.parser import IntentParser
from integrations.oauth_handler import GoogleOAuthHandler
from tools.registry import ToolRegistry

class TestGmailIntegration(unittest.TestCase):

    def setUp(self):
        self.parser = IntentParser()
        self.registry = ToolRegistry()
        self.oauth = GoogleOAuthHandler(token_file="test_token.json")

    def tearDown(self):
        if os.path.exists("test_token.json"):
            try:
                os.remove("test_token.json")
            except Exception:
                pass

    def test_oauth_mock_session_creation(self):
        self.assertFalse(self.oauth.is_authenticated())
        self.oauth.create_mock_authenticated_session("test.lead@enterprise.com")
        self.assertTrue(self.oauth.is_authenticated())
        self.assertEqual(self.oauth.get_authenticated_user_email(), "test.lead@enterprise.com")
        self.assertIsNotNone(self.oauth.get_access_token())

    def test_end_to_end_parse_and_tool_execution(self):
        """Simulates full workflow: Prompt -> Reasoning -> HITL Approval -> Tool Execution."""
        prompt = "Send an email to dr.sharma@university.edu saying Phase 1 is done."
        
        # 1. Parse prompt
        plan = self.parser.parse_instruction(prompt)
        self.assertFalse(plan.requires_clarification)
        self.assertEqual(plan.target_tool, "gmail_send_tool")
        
        # 2. Simulate User Modifying Subject in HITL draft review
        email_params = plan.tool_parameters
        email_params["subject"] = "BTech Major Project - Phase 1 Finalized"

        # 3. Simulate User Confirming and Dispatching Tool
        result = self.registry.execute_tool(
            tool_name=plan.target_tool,
            parameters=email_params,
            user_confirmed=True,
        )

        # 4. Verify Execution Result
        self.assertTrue(result.success)
        self.assertIsNotNone(result.external_reference_id)
        self.assertEqual(result.data["recipient"], "dr.sharma@university.edu")
        self.assertEqual(result.data["subject"], "BTech Major Project - Phase 1 Finalized")

if __name__ == "__main__":
    unittest.main()
