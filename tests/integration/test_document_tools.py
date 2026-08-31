"""
Integration tests for Document Tools registered in ToolRegistry.
"""

import unittest
from tools.registry import ToolRegistry
from tools.base import ToolSafetyLevel

class TestDocumentToolsIntegration(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry()
        self.sample_text = (
            "# Q3 Performance Report\n"
            "Total tasks processed: 1420.\n"
            "Customer satisfaction score: 98.4%.\n"
            "Server downtime: 0 hours."
        )

    def test_document_tools_registered(self):
        tool_names = self.registry.list_tool_names()
        self.assertIn("document_analyze_tool", tool_names)
        self.assertIn("document_edit_tool", tool_names)
        self.assertIn("document_convert_tool", tool_names)

        edit_tool = self.registry.get_tool("document_edit_tool")
        self.assertEqual(edit_tool.metadata.safety_level, ToolSafetyLevel.WRITE_SAFE)

    def test_execute_document_analyze_tool(self):
        result = self.registry.execute_tool(
            tool_name="document_analyze_tool",
            parameters={"text": self.sample_text, "filename": "report.md"},
            user_confirmed=False,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["filename"], "report.md")
        self.assertGreater(result.data["word_count"], 0)

    def test_execute_document_edit_tool_ai_command(self):
        result = self.registry.execute_tool(
            tool_name="document_edit_tool",
            parameters={"text": self.sample_text, "command": "Summarize this report"},
            user_confirmed=False,
        )
        self.assertTrue(result.success)
        self.assertIn("edited_text", result.data)
        self.assertIn("Executive Summary", result.data["edited_text"])

    def test_execute_document_convert_tool_pdf(self):
        result = self.registry.execute_tool(
            tool_name="document_convert_tool",
            parameters={"text": self.sample_text, "target_format": "pdf", "title": "Q3 Report"},
            user_confirmed=False,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["format"], "pdf")
        self.assertGreater(result.data["byte_size"], 100)

if __name__ == "__main__":
    unittest.main()
