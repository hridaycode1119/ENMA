"""
Gmail REST API Client and RFC 2822 MIME Assembly Engine.
"""

from __future__ import annotations
import base64
import json
import time
import urllib.error
import urllib.request
import uuid
from abc import ABC, abstractmethod
from email.message import EmailMessage
from typing import Any, Dict, List, Optional

from .oauth_handler import GoogleOAuthHandler

def create_mime_message(
    to: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    from_email: Optional[str] = None,
) -> Dict[str, str]:
    """
    Constructs an RFC 2822 compliant MIME message and encodes it as URL-safe base64.
    """
    msg = EmailMessage()
    msg["To"] = to.strip()
    msg["Subject"] = subject.strip()
    if from_email:
        msg["From"] = from_email.strip()

    msg.set_content(body_text)

    if body_html:
        msg.add_alternative(body_html, subtype="html")

    raw_bytes = msg.as_bytes()
    encoded_raw = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    return {"raw": encoded_raw}

class BaseGmailClient(ABC):
    """Abstract interface for Gmail operations."""

    @abstractmethod
    def send_message(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches email message."""
        pass

    @abstractmethod
    def create_draft(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates email draft."""
        pass

class MockGmailClient(BaseGmailClient):
    """
    In-memory simulated Gmail client for offline development,
    rapid test execution, and CI/CD environments.
    """

    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []
        self.draft_messages: List[Dict[str, Any]] = []

    def send_message(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> Dict[str, Any]:
        msg_id = f"18f9{uuid.uuid4().hex[:12]}"
        record = {
            "id": msg_id,
            "threadId": msg_id,
            "labelIds": ["SENT"],
            "to": to,
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html,
            "timestamp": time.time(),
        }
        self.sent_messages.append(record)
        return {"id": msg_id, "threadId": msg_id, "labelIds": ["SENT"]}

    def create_draft(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> Dict[str, Any]:
        draft_id = f"r-{uuid.uuid4().hex[:12]}"
        msg_id = f"18f9{uuid.uuid4().hex[:12]}"
        record = {
            "id": draft_id,
            "message": {
                "id": msg_id,
                "threadId": msg_id,
                "labelIds": ["DRAFT"],
            },
            "to": to,
            "subject": subject,
            "body_text": body_text,
            "timestamp": time.time(),
        }
        self.draft_messages.append(record)
        return {"id": draft_id, "message": {"id": msg_id, "threadId": msg_id, "labelIds": ["DRAFT"]}}

class GmailClient(BaseGmailClient):
    """
    Production REST API client interfacing with Google Gmail v1 endpoints.
    """

    def __init__(self, oauth_handler: Optional[GoogleOAuthHandler] = None):
        self.oauth = oauth_handler or GoogleOAuthHandler()
        self._mock_fallback = MockGmailClient()

    def send_message(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> Dict[str, Any]:
        access_token = self.oauth.get_access_token()
        if not access_token or access_token.startswith("mock_"):
            # Use deterministic mock client
            return self._mock_fallback.send_message(to, subject, body_text, body_html)

        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        payload = create_mime_message(to, subject, body_text, body_html)

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            raise RuntimeError(f"Gmail REST API Send Error {err.code}: {err.reason}")
        except Exception as ex:
            raise RuntimeError(f"Failed to communicate with Gmail REST API: {str(ex)}")

    def create_draft(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> Dict[str, Any]:
        access_token = self.oauth.get_access_token()
        if not access_token or access_token.startswith("mock_"):
            return self._mock_fallback.create_draft(to, subject, body_text, body_html)

        url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
        payload = {"message": create_mime_message(to, subject, body_text, body_html)}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as ex:
            raise RuntimeError(f"Failed to create draft in Gmail: {str(ex)}")
