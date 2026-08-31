"""
Unit tests for CalendarScheduleTool and meeting creation.
"""

import unittest
from tools.calendar.calendar_tool import CalendarScheduleTool
from tools.registry import ToolRegistry
from tools.base import ToolSafetyLevel

class TestCalendarTool(unittest.TestCase):

    def setUp(self):
        self.cal_tool = CalendarScheduleTool()
        self.registry = ToolRegistry()

    def test_calendar_tool_registered(self):
        tool = self.registry.get_tool("calendar_schedule_tool")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.metadata.safety_level, ToolSafetyLevel.WRITE_SAFE)

    def test_execute_calendar_schedule_success(self):
        params = {
            "title": "BTech Major Project Defense Preparation",
            "time": "Friday, 03:00 PM",
            "duration": "45 mins",
            "attendees": ["vaishnavi.d@example.com", "chetan@enterprise.com", "hriday@enterprise.com"],
        }
        result = self.cal_tool.execute(params)
        self.assertTrue(result.success)
        self.assertIn("meet_url", result.data)
        self.assertIn("https://meet.google.com/", result.data["meet_url"])
        self.assertEqual(result.data["title"], "BTech Major Project Defense Preparation")

    def test_list_events(self):
        events = self.cal_tool.list_today_events()
        self.assertGreaterEqual(len(events), 4)
        self.assertEqual(events[0]["title"], "Daily Standup")

if __name__ == "__main__":
    unittest.main()
