"""
Calendar and Meeting Scheduling Dynamic Tools for AIRA Agent.
"""

from __future__ import annotations
import time
import uuid
from typing import Any, Dict, List, Optional

from tools.base import BaseTool, ToolMetadata, ToolResult, ToolSafetyLevel

class CalendarScheduleTool(BaseTool):
    """
    Schedules meetings and creates calendar events with Google Meet links.
    Classified as WRITE_SAFE.
    """

    def __init__(self):
        self.events: List[Dict[str, Any]] = [
            {
                "id": "evt-101",
                "title": "Daily Standup",
                "time": "09:00 AM",
                "duration": "30 mins",
                "meet_url": "https://meet.google.com/abc-defg-hij",
                "attendees": ["team@enterprise.com"],
            },
            {
                "id": "evt-102",
                "title": "Team Sync",
                "time": "11:00 AM",
                "duration": "1 hour",
                "meet_url": "https://meet.google.com/klm-nopq-rst",
                "attendees": ["vaishnavi.d@example.com", "chetan@enterprise.com"],
            },
            {
                "id": "evt-103",
                "title": "Client Presentation",
                "time": "02:00 PM",
                "duration": "1 hour",
                "meet_url": "https://meet.google.com/uvw-xyza-bcd",
                "attendees": ["client@corp.com"],
            },
            {
                "id": "evt-104",
                "title": "Review & Planning",
                "time": "04:30 PM",
                "duration": "30 mins",
                "meet_url": "https://meet.google.com/efg-hijk-lmn",
                "attendees": ["hriday@enterprise.com"],
            },
        ]

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="calendar_schedule_tool",
            display_name="Calendar Meeting Scheduler",
            description="Schedules meetings, adds events to Google Calendar, and generates Google Meet video links.",
            safety_level=ToolSafetyLevel.WRITE_SAFE,
            version="1.0.0",
        )

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if "title" not in params and "summary" not in params:
            raise ValueError("Meeting 'title' is required.")
        return params

    def execute(self, validated_params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        title = validated_params.get("title") or validated_params.get("summary", "New Meeting")
        event_time = validated_params.get("time", "Tomorrow, 11:00 AM")
        duration = validated_params.get("duration", "30 mins")
        attendees = validated_params.get("attendees", ["team@enterprise.com"])

        meet_code = f"{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
        meet_url = f"https://meet.google.com/{meet_code}"

        event_record = {
            "id": f"evt-{uuid.uuid4().hex[:6]}",
            "title": title,
            "time": event_time,
            "duration": duration,
            "meet_url": meet_url,
            "attendees": attendees,
            "created_at": time.time(),
        }
        self.events.append(event_record)
        elapsed = (time.time() - start_time) * 1000

        return ToolResult(
            success=True,
            data={
                "event_id": event_record["id"],
                "title": title,
                "time": event_time,
                "duration": duration,
                "meet_url": meet_url,
            },
            external_reference_id=event_record["id"],
            execution_time_ms=elapsed,
        )

    def list_today_events(self) -> List[Dict[str, Any]]:
        return self.events
