"""
Task and Intent Schemas for the Autonomous AI Agent.
Supports both Pydantic v2 validation (when available) and standard library fallback.
"""

from __future__ import annotations
import json
import re
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

# Regular expression for robust email address verification
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

class TaskType(str, Enum):
    """Supported enterprise task classifications."""
    EMAIL_SEND = "EMAIL_SEND"
    EMAIL_DRAFT = "EMAIL_DRAFT"
    DOCUMENT_CREATE = "DOCUMENT_CREATE"
    CALENDAR_SCHEDULE = "CALENDAR_SCHEDULE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> "TaskType":
        try:
            return cls(value.upper().strip())
        except (ValueError, AttributeError):
            return cls.UNKNOWN

class EmailTone(str, Enum):
    """Tone options for drafted communications."""
    FORMAL = "formal"
    PROFESSIONAL = "professional"
    URGENT = "urgent"
    CASUAL = "casual"

    @classmethod
    def from_str(cls, value: str) -> "EmailTone":
        try:
            return cls(value.lower().strip())
        except (ValueError, AttributeError):
            return cls.PROFESSIONAL

class EmailPriority(str, Enum):
    """Priority classifications for email dispatch."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

    @classmethod
    def from_str(cls, value: str) -> "EmailPriority":
        try:
            return cls(value.lower().strip())
        except (ValueError, AttributeError):
            return cls.NORMAL

class EmailDraftPayload:
    """Structured payload containing parameters for an email draft or dispatch."""

    def __init__(
        self,
        recipient_email: str,
        subject: str,
        body_text: str,
        recipient_name: Optional[str] = None,
        body_html: Optional[str] = None,
        tone: EmailTone | str = EmailTone.PROFESSIONAL,
        priority: EmailPriority | str = EmailPriority.NORMAL,
    ):
        self.recipient_email = self._validate_email(recipient_email)
        self.recipient_name = recipient_name.strip() if recipient_name else None
        self.subject = self._validate_subject(subject)
        self.body_text = self._validate_body(body_text)
        self.body_html = body_html or self._default_html(self.body_text)
        self.tone = tone if isinstance(tone, EmailTone) else EmailTone.from_str(tone)
        self.priority = (
            priority if isinstance(priority, EmailPriority) else EmailPriority.from_str(priority)
        )

    @staticmethod
    def _validate_email(email: str) -> str:
        if not email or not isinstance(email, str):
            raise ValueError("Recipient email must be a non-empty string.")
        cleaned = email.strip()
        if not EMAIL_REGEX.match(cleaned):
            raise ValueError(f"Invalid email address format: '{email}'")
        return cleaned

    @staticmethod
    def _validate_subject(subject: str) -> str:
        if not subject or not isinstance(subject, str):
            raise ValueError("Subject must be a non-empty string.")
        cleaned = subject.strip()
        if len(cleaned) < 2:
            raise ValueError("Subject must be at least 2 characters long.")
        return cleaned

    @staticmethod
    def _validate_body(body: str) -> str:
        if not body or not isinstance(body, str):
            raise ValueError("Body text must be a non-empty string.")
        cleaned = body.strip()
        if len(cleaned) < 5:
            raise ValueError("Body text must be at least 5 characters long.")
        return cleaned

    @staticmethod
    def _default_html(plain_text: str) -> str:
        """Converts plain text linebreaks to standard HTML paragraphs."""
        paragraphs = plain_text.split("\n\n")
        html_parts = []
        for p in paragraphs:
            lines = p.replace("\n", "<br/>")
            html_parts.append(f"<p>{lines}</p>")
        return "".join(html_parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recipient_email": self.recipient_email,
            "recipient_name": self.recipient_name,
            "subject": self.subject,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "tone": self.tone.value,
            "priority": self.priority.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmailDraftPayload":
        return cls(
            recipient_email=data.get("recipient_email", ""),
            recipient_name=data.get("recipient_name"),
            subject=data.get("subject", ""),
            body_text=data.get("body_text", ""),
            body_html=data.get("body_html"),
            tone=data.get("tone", EmailTone.PROFESSIONAL),
            priority=data.get("priority", EmailPriority.NORMAL),
        )

    def __repr__(self) -> str:
        return f"<EmailDraftPayload to='{self.recipient_email}' subject='{self.subject}'>"

class ClarificationRequest:
    """Encapsulates missing entity prompts when user input is incomplete."""

    def __init__(
        self,
        missing_fields: List[str],
        question_for_user: str,
        suggested_defaults: Optional[Dict[str, Any]] = None,
    ):
        self.missing_fields = missing_fields or []
        self.question_for_user = question_for_user.strip()
        self.suggested_defaults = suggested_defaults or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missing_fields": self.missing_fields,
            "question_for_user": self.question_for_user,
            "suggested_defaults": self.suggested_defaults,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClarificationRequest":
        return cls(
            missing_fields=data.get("missing_fields", []),
            question_for_user=data.get("question_for_user", ""),
            suggested_defaults=data.get("suggested_defaults", {}),
        )

    def __repr__(self) -> str:
        return f"<ClarificationRequest missing={self.missing_fields} question='{self.question_for_user}'>"

class TaskPlan:
    """Deterministic structured plan synthesized by the reasoning agent."""

    def __init__(
        self,
        task_id: Optional[str] = None,
        task_type: TaskType | str = TaskType.EMAIL_SEND,
        intent_summary: str = "",
        confidence: float = 1.0,
        requires_clarification: bool = False,
        clarification: Optional[ClarificationRequest] = None,
        target_tool: str = "gmail_send_tool",
        tool_parameters: Optional[Dict[str, Any]] = None,
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.task_type = (
            task_type if isinstance(task_type, TaskType) else TaskType.from_str(task_type)
        )
        self.intent_summary = intent_summary.strip()
        self.confidence = max(0.0, min(1.0, float(confidence)))
        self.requires_clarification = bool(requires_clarification)
        self.clarification = clarification
        self.target_tool = target_tool.strip()
        self.tool_parameters = tool_parameters or {}

    def get_email_payload(self) -> Optional[EmailDraftPayload]:
        """Convenience accessor to instantiate validated EmailDraftPayload from tool_parameters."""
        if not self.tool_parameters:
            return None
        try:
            return EmailDraftPayload.from_dict(self.tool_parameters)
        except Exception:
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "intent_summary": self.intent_summary,
            "confidence": self.confidence,
            "requires_clarification": self.requires_clarification,
            "clarification": self.clarification.to_dict() if self.clarification else None,
            "target_tool": self.target_tool,
            "tool_parameters": self.tool_parameters,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskPlan":
        clarification_data = data.get("clarification")
        clarification_obj = (
            ClarificationRequest.from_dict(clarification_data)
            if clarification_data
            else None
        )
        return cls(
            task_id=data.get("task_id"),
            task_type=data.get("task_type", TaskType.EMAIL_SEND),
            intent_summary=data.get("intent_summary", ""),
            confidence=data.get("confidence", 1.0),
            requires_clarification=data.get("requires_clarification", False),
            clarification=clarification_obj,
            target_tool=data.get("target_tool", "gmail_send_tool"),
            tool_parameters=data.get("tool_parameters", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "TaskPlan":
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return f"<TaskPlan id='{self.task_id}' type='{self.task_type.value}' clarify={self.requires_clarification}>"

class AgentDecision:
    """Top-level LLM reasoning output contract."""

    def __init__(
        self,
        task_plan: TaskPlan,
        raw_reasoning: Optional[str] = None,
    ):
        self.task_plan = task_plan
        self.raw_reasoning = raw_reasoning

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_plan": self.task_plan.to_dict(),
            "raw_reasoning": self.raw_reasoning,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentDecision":
        plan_data = data.get("task_plan", data)
        return cls(
            task_plan=TaskPlan.from_dict(plan_data),
            raw_reasoning=data.get("raw_reasoning"),
        )
