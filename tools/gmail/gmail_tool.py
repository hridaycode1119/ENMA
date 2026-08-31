"""
Concrete Gmail Tool Implementations: GmailSendTool and GmailDraftTool.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional

from integrations.gmail_client import BaseGmailClient, GmailClient
from schemas.task_schemas import EmailDraftPayload
from tools.base import BaseTool, ToolMetadata, ToolResult, ToolSafetyLevel

class GmailSendTool(BaseTool):
    """
    Executes live email dispatch via authorized Gmail REST API.
    Classified as CONSEQUENTIAL (requires human confirmation).
    """

    def __init__(self, client: Optional[BaseGmailClient] = None):
        self.client = client or GmailClient()

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="gmail_send_tool",
            display_name="Gmail Live Dispatcher",
            description="Sends an email to the designated recipient via the authorized Gmail REST API.",
            safety_level=ToolSafetyLevel.CONSEQUENTIAL,
            version="1.0.0",
        )

    def validate_parameters(self, params: Dict[str, Any]) -> EmailDraftPayload:
        if isinstance(params, EmailDraftPayload):
            return params
        return EmailDraftPayload.from_dict(params)

    def execute(self, validated_params: EmailDraftPayload | Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        try:
            payload = self.validate_parameters(validated_params)
            response = self.client.send_message(
                to=payload.recipient_email,
                subject=payload.subject,
                body_text=payload.body_text,
                body_html=payload.body_html,
            )
            elapsed_ms = (time.time() - start_time) * 1000
            msg_id = response.get("id")

            return ToolResult(
                success=True,
                data={
                    "message_id": msg_id,
                    "thread_id": response.get("threadId"),
                    "recipient": payload.recipient_email,
                    "subject": payload.subject,
                },
                external_reference_id=msg_id,
                execution_time_ms=elapsed_ms,
            )
        except Exception as ex:
            elapsed_ms = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                error_message=str(ex),
                execution_time_ms=elapsed_ms,
            )

class GmailDraftTool(BaseTool):
    """
    Creates a draft in the user's Gmail mailbox without sending.
    Classified as WRITE_SAFE (non-destructive).
    """

    def __init__(self, client: Optional[BaseGmailClient] = None):
        self.client = client or GmailClient()

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="gmail_draft_tool",
            display_name="Gmail Draft Creator",
            description="Saves a message draft into the user's Gmail mailbox.",
            safety_level=ToolSafetyLevel.WRITE_SAFE,
            version="1.0.0",
        )

    def validate_parameters(self, params: Dict[str, Any]) -> EmailDraftPayload:
        if isinstance(params, EmailDraftPayload):
            return params
        return EmailDraftPayload.from_dict(params)

    def execute(self, validated_params: EmailDraftPayload | Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        try:
            payload = self.validate_parameters(validated_params)
            response = self.client.create_draft(
                to=payload.recipient_email,
                subject=payload.subject,
                body_text=payload.body_text,
                body_html=payload.body_html,
            )
            elapsed_ms = (time.time() - start_time) * 1000
            draft_id = response.get("id")

            return ToolResult(
                success=True,
                data={
                    "draft_id": draft_id,
                    "message_id": response.get("message", {}).get("id"),
                    "recipient": payload.recipient_email,
                    "subject": payload.subject,
                },
                external_reference_id=draft_id,
                execution_time_ms=elapsed_ms,
            )
        except Exception as ex:
            elapsed_ms = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                error_message=str(ex),
                execution_time_ms=elapsed_ms,
            )
