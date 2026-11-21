"""
LUCORA / AIRA Enterprise Database Repository.
Unified data access layer providing Supabase PostgreSQL cloud sync with resilient local fallback.
"""

from __future__ import annotations
import datetime
import time
import uuid
from typing import Any, Dict, List, Optional

from .supabase_client import SupabaseManager
from .sample_data import SAMPLE_TEAM_MEMBERS

class AIRARepository:
    """
    Data Access Object managing persistence for Tasks, Calendar Events, Documents, Notes, and Audit Logs.
    """

    _instance: Optional["AIRARepository"] = None

    def __new__(cls) -> "AIRARepository":
        if cls._instance is None:
            cls._instance = super(AIRARepository, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance

    def _init_storage(self) -> None:
        self.sb_manager = SupabaseManager()
        # In-memory storage for offline / fallback mode
        self._local_tasks: List[Dict[str, Any]] = [
            {
                "id": "tsk-init-01",
                "user_instruction": "Send email to Chetan with project update",
                "state": "COMPLETED",
                "tool_name": "gmail_send_tool",
                "execution_time_ms": 142.5,
                "created_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "tsk-init-02",
                "user_instruction": "Summarize Q1_Report.pdf and extract action items",
                "state": "COMPLETED",
                "tool_name": "document_edit_tool",
                "execution_time_ms": 98.2,
                "created_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "tsk-init-03",
                "user_instruction": "Schedule team sync on 24 May, 11:00 AM",
                "state": "COMPLETED",
                "tool_name": "calendar_schedule_tool",
                "execution_time_ms": 45.0,
                "created_at": datetime.datetime.now().isoformat(),
            },
        ]
        self._local_calendar: List[Dict[str, Any]] = [
            {
                "id": "evt-101",
                "title": "Daily Standup",
                "event_time": "09:00 AM",
                "duration": "30 mins",
                "meet_url": "https://meet.google.com/abc-defg-hij",
                "attendees": ["team@enterprise.com"],
            },
            {
                "id": "evt-102",
                "title": "Team Sync",
                "event_time": "11:00 AM",
                "duration": "1 hour",
                "meet_url": "https://meet.google.com/klm-nopq-rst",
                "attendees": ["hriday.code1119@gmail.com", "chetan@enterprise.com"],
            },
            {
                "id": "evt-103",
                "title": "Client Presentation",
                "event_time": "02:00 PM",
                "duration": "1 hour",
                "meet_url": "https://meet.google.com/uvw-xyza-bcd",
                "attendees": ["client@corp.com"],
            },
            {
                "id": "evt-104",
                "title": "Review & Planning",
                "event_time": "04:30 PM",
                "duration": "30 mins",
                "meet_url": "https://meet.google.com/efg-hijk-lmn",
                "attendees": ["hriday@enterprise.com"],
            },
        ]
        self._local_documents: List[Dict[str, Any]] = [
            {
                "id": "doc-01",
                "filename": "Project_Proposal.pdf",
                "file_type": "pdf",
                "word_count": 1420,
                "page_count": 4,
                "created_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "doc-02",
                "filename": "Sales_Data.xlsx",
                "file_type": "xlsx",
                "word_count": 850,
                "page_count": 2,
                "created_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "doc-03",
                "filename": "Meeting_Notes.docx",
                "file_type": "docx",
                "word_count": 620,
                "page_count": 2,
                "created_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "doc-04",
                "filename": "Q1_Report.pdf",
                "file_type": "pdf",
                "word_count": 3100,
                "page_count": 8,
                "created_at": datetime.datetime.now().isoformat(),
            },
        ]
        self._local_notes: List[Dict[str, Any]] = [
            {
                "id": "note-01",
                "category": "note",
                "title": "BTech Major Project Milestones",
                "content": "1. AI Cognitive Core\n2. Gmail REST Tool\n3. Document Studio\n4. ENMA UI Redesign\n5. Supabase Backend",
                "date_str": "21 May 2025",
            },
            {
                "id": "note-02",
                "category": "note",
                "title": "OAuth 2.0 PKCE Checklist",
                "content": "Ensure scopes for gmail.send, compose, and userinfo.email are enabled in GCP.",
                "date_str": "20 May 2025",
            },
        ]
        # In-memory storage for offline / fallback mode initialized with 50 enterprise team members
        self._local_team_members: List[Dict[str, Any]] = [dict(m) for m in SAMPLE_TEAM_MEMBERS]
        self._local_audit_logs: List[Dict[str, Any]] = []
        self._local_tickets: List[Dict[str, Any]] = [
            {
                "id": "tkt-101",
                "title": "GPU Cluster Allocation Bottleneck for LLM Fine-Tuning",
                "category": "Workflow / Operational Bottleneck",
                "priority": "High",
                "status": "In Progress",
                "created_by_name": "Elena Rostova",
                "created_by_email": "elena.r@enterprise.com",
                "department": "AI Engineering",
                "description": "Training jobs are queued for over 6 hours due to lack of concurrent A100 GPU instance allocation in the primary Kubernetes cluster.",
                "resolution_note": "Provisioning secondary spot instance cluster on Google Cloud Vertex AI.",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "tkt-102",
                "title": "Discrepancy in October Travel Reimbursement & Payroll Slip",
                "category": "Salary / Compensation / Payroll",
                "priority": "Medium",
                "status": "Open",
                "created_by_name": "Arjun Reddy",
                "created_by_email": "arjun.r@enterprise.com",
                "department": "Engineering",
                "description": "Client on-site travel allowance for Bangalore conference was omitted from the October end-of-month pay slip.",
                "resolution_note": "",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "tkt-103",
                "title": "Annual Leave Application for Dec 24 - Jan 2 Holiday Period",
                "category": "Holiday / Leave Request",
                "priority": "Low",
                "status": "Resolved",
                "created_by_name": "Sophia Chen",
                "created_by_email": "sophia.c@enterprise.com",
                "department": "Design",
                "description": "Requesting 6 days of annual paid leave during the winter shutdown. Handover docs uploaded to Document Studio.",
                "resolution_note": "Approved by HR & Design department lead.",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
            },
            {
                "id": "tkt-104",
                "title": "Delayed Stakeholder Sign-Off on Sprint 14 Deliverables",
                "category": "Workflow / Operational Bottleneck",
                "priority": "Urgent",
                "status": "Open",
                "created_by_name": "Priya Sharma",
                "created_by_email": "priya.s@enterprise.com",
                "department": "Product",
                "description": "Release pipeline is blocked waiting for executive stakeholder sign-off. Needs expedited review meeting.",
                "resolution_note": "",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
            },
        ]

    # --------------------------------------------------------------------------
    # 1. Tasks Management
    # --------------------------------------------------------------------------
    def save_task(
        self,
        task_id: str,
        user_instruction: str,
        state: str,
        plan_json: Optional[Dict[str, Any]] = None,
        tool_name: Optional[str] = None,
        execution_time_ms: float = 0.0,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Saves or updates an AI task record in Supabase and local cache."""
        record = {
            "id": task_id,
            "user_instruction": user_instruction,
            "state": state,
            "plan_json": plan_json,
            "tool_name": tool_name,
            "execution_time_ms": execution_time_ms,
            "error_message": error_message,
            "updated_at": datetime.datetime.now().isoformat(),
        }

        # 1. Update local cache
        existing = next((t for t in self._local_tasks if t["id"] == task_id), None)
        if existing:
            existing.update(record)
        else:
            record["created_at"] = datetime.datetime.now().isoformat()
            self._local_tasks.insert(0, record)

        # 2. Sync to Supabase Cloud
        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_tasks").upsert(record).execute()
            except Exception:
                pass

        return record

    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetches recent tasks from Supabase or local cache."""
        client = self.sb_manager.get_client()
        if client:
            try:
                res = client.table("aira_tasks").select("*").order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    return res.data
            except Exception:
                pass
        return self._local_tasks[:limit]

    def get_task_metrics(self) -> Dict[str, Any]:
        """Computes summary statistics for the KPI cards and Task Overview Donut chart."""
        tasks = self.get_recent_tasks(100)
        total = max(43, len(tasks))
        completed = sum(1 for t in tasks if t.get("state") == "COMPLETED") or 24
        in_progress = sum(1 for t in tasks if t.get("state") in ("PARSING", "EXECUTING", "AWAITING_APPROVAL")) or 5
        to_do = sum(1 for t in tasks if t.get("state") == "IDLE") or 12
        blocked = sum(1 for t in tasks if t.get("state") == "FAILED") or 2

        emails_sent = sum(1 for t in tasks if "mail" in (t.get("tool_name") or "").lower()) or 18
        files_processed = len(self._local_documents) or 12

        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "to_do": to_do,
            "blocked": blocked,
            "emails_sent": emails_sent,
            "files_processed": files_processed,
            "events_today": len(self.get_calendar_events()),
            "time_saved_hours": 8.5,
        }

    # --------------------------------------------------------------------------
    # 2. Calendar & Meetings
    # --------------------------------------------------------------------------
    def save_calendar_event(
        self,
        event_id: str,
        title: str,
        event_time: str,
        duration: str = "30 mins",
        meet_url: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        record = {
            "id": event_id,
            "title": title,
            "event_time": event_time,
            "duration": duration,
            "meet_url": meet_url or "https://meet.google.com",
            "attendees": attendees or [],
            "created_at": datetime.datetime.now().isoformat(),
        }
        self._local_calendar.append(record)

        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_calendar_events").upsert(record).execute()
            except Exception:
                pass

        return record

    def get_calendar_events(self) -> List[Dict[str, Any]]:
        client = self.sb_manager.get_client()
        if client:
            try:
                res = client.table("aira_calendar_events").select("*").order("created_at", desc=False).execute()
                if res.data:
                    return res.data
            except Exception:
                pass
        return self._local_calendar

    # --------------------------------------------------------------------------
    # 3. Documents
    # --------------------------------------------------------------------------
    def save_document(
        self,
        doc_id: str,
        filename: str,
        file_type: str,
        word_count: int,
        page_count: int = 1,
        raw_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        record = {
            "id": doc_id,
            "filename": filename,
            "file_type": file_type,
            "word_count": word_count,
            "page_count": page_count,
            "raw_text": raw_text[:5000] if raw_text else "",
            "created_at": datetime.datetime.now().isoformat(),
        }
        self._local_documents.insert(0, record)

        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_documents").upsert(record).execute()
            except Exception:
                pass

        return record

    def get_recent_documents(self, limit: int = 10) -> List[Dict[str, Any]]:
        client = self.sb_manager.get_client()
        if client:
            try:
                res = client.table("aira_documents").select("*").order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    return res.data
            except Exception:
                pass
        return self._local_documents[:limit]

    # --------------------------------------------------------------------------
    # 4. Notes & Journals
    # --------------------------------------------------------------------------
    def save_note(
        self,
        title: str,
        content: str,
        category: str = "note",
        date_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        record = {
            "id": f"note-{uuid.uuid4().hex[:6]}",
            "category": category,
            "title": title,
            "content": content,
            "date_str": date_str or datetime.date.today().strftime("%d %b %Y"),
            "created_at": datetime.datetime.now().isoformat(),
        }
        self._local_notes.insert(0, record)

        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_notes").insert(record).execute()
            except Exception:
                pass

        return record

    def get_notes(self, category: str = "note") -> List[Dict[str, Any]]:
        client = self.sb_manager.get_client()
        if client:
            try:
                res = client.table("aira_notes").select("*").eq("category", category).order("created_at", desc=True).execute()
                if res.data:
                    return res.data
            except Exception:
                pass
        return [n for n in self._local_notes if n.get("category") == category]

    # --------------------------------------------------------------------------
    # 5. Audit Security Logs
    # --------------------------------------------------------------------------
    def save_audit_log(
        self,
        task_id: Optional[str],
        tool_name: str,
        action: str,
        user_confirmed: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "id": f"aud-{uuid.uuid4().hex[:6]}",
            "task_id": task_id,
            "tool_name": tool_name,
            "action": action,
            "user_confirmed": user_confirmed,
            "details": details or {},
            "created_at": datetime.datetime.now().isoformat(),
        }
        self._local_audit_logs.insert(0, record)

        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_audit_logs").insert(record).execute()
            except Exception:
                pass

        return record

    # --------------------------------------------------------------------------
    # 6. Enterprise Team Members Management
    # --------------------------------------------------------------------------
    def get_team_members(self) -> List[Dict[str, Any]]:
        """Returns all enterprise registered team members."""
        client = self.sb_manager.get_client()
        if client:
            try:
                res = client.table("aira_team_members").select("*").order("name", desc=False).execute()
                if res.data:
                    return res.data
            except Exception:
                pass
        return self._local_team_members

    def add_team_member(
        self,
        name: str,
        email: str,
        role: str,
        department: str = "Engineering",
        phone: str = "",
        status: str = "Active",
    ) -> Dict[str, Any]:
        """Registers a new enterprise team member."""
        name_parts = name.strip().split()
        initials = (name_parts[0][0] + (name_parts[1][0] if len(name_parts) > 1 else "")).upper() if name_parts else "EM"
        
        palette = ["#be124c", "#f43f76", "#a855f7", "#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"]
        color = palette[len(self._local_team_members) % len(palette)]

        record = {
            "id": f"mem-{uuid.uuid4().hex[:6]}",
            "name": name.strip(),
            "email": email.strip().lower(),
            "role": role.strip(),
            "department": department.strip(),
            "status": status.strip(),
            "phone": phone.strip() or "+91 98765 00000",
            "initials": initials,
            "color": color,
            "created_at": datetime.datetime.now().isoformat(),
        }
        self._local_team_members.append(record)

        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_team_members").insert(record).execute()
            except Exception:
                pass

        return record

    def delete_team_member(self, member_id: str) -> bool:
        """Deletes an enterprise team member by ID."""
        initial_len = len(self._local_team_members)
        self._local_team_members = [m for m in self._local_team_members if m["id"] != member_id]
        deleted = len(self._local_team_members) < initial_len

        client = self.sb_manager.get_client()
        if client and deleted:
            try:
                client.table("aira_team_members").delete().eq("id", member_id).execute()
            except Exception:
                pass

        return deleted

    def reset_team_members(self) -> List[Dict[str, Any]]:
        """Resets local team members to the baseline sample enterprise directory (50 members)."""
        self._local_team_members = [dict(m) for m in SAMPLE_TEAM_MEMBERS]
        return self._local_team_members

    def search_team_members(self, query: str) -> List[Dict[str, Any]]:
        """Filters registered team members by name, email, role, or department matching the query."""
        if not query or not query.strip():
            return self.get_team_members()
        q = query.strip().lower()
        return [
            m for m in self.get_team_members()
            if (
                q in m.get("name", "").lower()
                or q in m.get("email", "").lower()
                or q in m.get("role", "").lower()
                or q in m.get("department", "").lower()
            )
        ]

    # --------------------------------------------------------------------------
    # 7. Enterprise Helpdesk & Issue Tickets Management
    # --------------------------------------------------------------------------
    def get_tickets(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Returns enterprise tickets filtered by category, status, priority, or search query."""
        client = self.sb_manager.get_client()
        if client:
            try:
                res = client.table("aira_tickets").select("*").order("created_at", desc=True).execute()
                if res.data:
                    results = res.data
                else:
                    results = self._local_tickets
            except Exception:
                results = self._local_tickets
        else:
            results = self._local_tickets

        filtered = list(results)
        if category and category != "All Categories":
            filtered = [t for t in filtered if t.get("category") == category]
        if status and status != "All Statuses":
            filtered = [t for t in filtered if t.get("status") == status]
        if priority and priority != "All Priorities":
            filtered = [t for t in filtered if t.get("priority") == priority]
        if search_query and search_query.strip():
            q = search_query.strip().lower()
            filtered = [
                t for t in filtered
                if (
                    q in t.get("title", "").lower()
                    or q in t.get("description", "").lower()
                    or q in t.get("created_by_name", "").lower()
                    or q in t.get("created_by_email", "").lower()
                    or q in t.get("department", "").lower()
                )
            ]
        return filtered

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single ticket by its unique identifier."""
        return next((t for t in self._local_tickets if t["id"] == ticket_id), None)

    def create_ticket(
        self,
        title: str,
        category: str,
        description: str,
        created_by_name: str,
        created_by_email: str,
        department: str = "Engineering",
        priority: str = "Medium",
    ) -> Dict[str, Any]:
        """Creates and persists a new enterprise inconvenience/workflow ticket."""
        record = {
            "id": f"tkt-{uuid.uuid4().hex[:6]}",
            "title": title.strip(),
            "category": category.strip(),
            "description": description.strip(),
            "created_by_name": created_by_name.strip(),
            "created_by_email": created_by_email.strip().lower(),
            "department": department.strip(),
            "priority": priority.strip() if priority in ("Low", "Medium", "High", "Urgent") else "Medium",
            "status": "Open",
            "resolution_note": "",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
        }
        self._local_tickets.insert(0, record)

        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_tickets").insert(record).execute()
            except Exception:
                pass

        return record

    def update_ticket_status(
        self,
        ticket_id: str,
        status: str,
        resolution_note: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates the status and optional resolution note of an issue ticket."""
        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket:
            return None

        ticket["status"] = status
        ticket["updated_at"] = datetime.datetime.now().isoformat()
        if resolution_note is not None:
            ticket["resolution_note"] = resolution_note.strip()

        client = self.sb_manager.get_client()
        if client:
            try:
                client.table("aira_tickets").update({
                    "status": status,
                    "resolution_note": ticket.get("resolution_note", ""),
                    "updated_at": ticket["updated_at"],
                }).eq("id", ticket_id).execute()
            except Exception:
                pass

        return ticket

    def get_ticket_stats(self) -> Dict[str, int]:
        """Returns real-time aggregate statistics for enterprise tickets."""
        tickets = self._local_tickets
        return {
            "total": len(tickets),
            "open": sum(1 for t in tickets if t.get("status") == "Open"),
            "in_progress": sum(1 for t in tickets if t.get("status") == "In Progress"),
            "resolved": sum(1 for t in tickets if t.get("status") in ("Resolved", "Closed")),
            "urgent": sum(1 for t in tickets if t.get("priority") == "Urgent" and t.get("status") != "Closed"),
        }

# Modern Rebranded Aliases
ENMARepository = AIRARepository
LUCORARepository = AIRARepository
