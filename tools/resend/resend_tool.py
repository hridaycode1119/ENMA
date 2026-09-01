"""
Resend Email Dispatch Dynamic Tool for AIRA Agent.
Classified as CONSEQUENTIAL (requires Human-in-the-Loop approval before live dispatch).
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional

from tools.base import BaseTool, ToolMetadata, ToolResult, ToolSafetyLevel
from integrations.resend_client import ResendClient
from database.repository import AIRARepository

class ResendSendTool(BaseTool):
    """
    Sends verified emails via Resend REST API.
    Protected by Human-in-the-Loop approval gate (CONSEQUENTIAL).
    """

    def __init__(self, resend_client: Optional[ResendClient] = None):
        self.client = resend_client or ResendClient()

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="resend_send_tool",
            display_name="Resend Email Dispatcher",
            description="Sends transactional and AI-generated emails directly to recipient mailboxes via Resend REST API.",
            safety_level=ToolSafetyLevel.CONSEQUENTIAL,
            version="1.0.0",
        )

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        to = params.get("to") or params.get("recipient")
        if not to:
            raise ValueError("Recipient email ('to') is required.")

        subject = params.get("subject", "").strip()
        if not subject:
            raise ValueError("Email 'subject' is required.")

        body = params.get("body", "").strip()
        if not body:
            raise ValueError("Email 'body' is required.")

        return {
            "to": to,
            "subject": subject,
            "body": body,
            "from_email": params.get("from_email"),
            "reply_to": params.get("reply_to"),
        }

    def execute(self, validated_params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        to = validated_params["to"]
        subject = validated_params["subject"]
        body = validated_params["body"]
        from_email = validated_params.get("from_email")
        reply_to = validated_params.get("reply_to")

        try:
            response = self.client.send_email(
                to=to,
                subject=subject,
                text=body,
                from_email=from_email,
                reply_to=reply_to,
            )
            elapsed_ms = (time.time() - start_time) * 1000

            # Record in repository
            repo = AIRARepository()
            repo.save_audit_log(
                task_id=response.get("id"),
                tool_name="resend_send_tool",
                action="email_sent",
                user_confirmed=True,
                details=response,
            )

            return ToolResult(
                success=True,
                data=response,
                external_reference_id=response.get("id"),
                execution_time_ms=elapsed_ms,
            )

        except Exception as ex:
            elapsed_ms = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                error_message=f"Failed to dispatch email via Resend: {str(ex)}",
                execution_time_ms=elapsed_ms,
            )
