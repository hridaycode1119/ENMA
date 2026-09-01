"""
Resend Email API Client for AIRA Autonomous AI Agent.
Provides modern, reliable transactional & automated email delivery with HTML template rendering.
"""

from __future__ import annotations
import os
import uuid
import time
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import resend
    HAS_RESEND_LIB = True
except ImportError:
    HAS_RESEND_LIB = False
    resend = None

class ResendClient:
    """
    Wrapper around the official Resend Python SDK.
    Supports live email dispatch and safe mock fallback mode.
    """

    _instance: Optional["ResendClient"] = None

    def __new__(cls, api_key: Optional[str] = None, from_email: Optional[str] = None) -> "ResendClient":
        if cls._instance is None:
            cls._instance = super(ResendClient, cls).__new__(cls)
            cls._instance._init_client(api_key, from_email)
        elif api_key:
            cls._instance.configure(api_key, from_email)
        return cls._instance

    def _init_client(self, api_key: Optional[str] = None, from_email: Optional[str] = None) -> None:
        self.api_key = (api_key or os.getenv("RESEND_API_KEY", "")).strip()
        self.default_from = (from_email or os.getenv("RESEND_FROM_EMAIL", "AIRA AI <onboarding@resend.dev>")).strip()
        if HAS_RESEND_LIB and self.api_key:
            resend.api_key = self.api_key

    def configure(self, api_key: str, from_email: Optional[str] = None) -> None:
        """Configures or updates the Resend API credentials at runtime."""
        self.api_key = api_key.strip()
        if from_email:
            self.default_from = from_email.strip()
        os.environ["RESEND_API_KEY"] = self.api_key
        os.environ["RESEND_FROM_EMAIL"] = self.default_from
        if HAS_RESEND_LIB and self.api_key:
            resend.api_key = self.api_key

    def is_configured(self) -> bool:
        """Returns True if a valid Resend API key is configured."""
        return bool(self.api_key and self.api_key.startswith("re_"))

    def send_email(
        self,
        to: str | List[str],
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches an email via Resend REST API or simulates successful dispatch in mock mode.
        """
        recipients = [to] if isinstance(to, str) else to
        sender = from_email or self.default_from

        if not text and not html:
            text = "(No content provided)"

        if not html and text:
            # Generate clean styled HTML template
            html = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 10px; background-color: #ffffff;">
                <div style="font-size: 16px; line-height: 1.6; color: #1a1a1a; white-space: pre-wrap;">{text}</div>
                <hr style="border: none; border-top: 1px solid #eaeaea; margin: 24px 0;" />
                <div style="font-size: 12px; color: #888888; text-align: center;">
                    ⚡ Sent autonomously via <strong>AIRA Enterprise AI Agent</strong> powered by <strong>Resend</strong>
                </div>
            </div>
            """

        params: Dict[str, Any] = {
            "from": sender,
            "to": recipients,
            "subject": subject,
            "html": html,
            "text": text or "",
        }

        if reply_to:
            params["reply_to"] = reply_to
        if cc:
            params["cc"] = cc
        if bcc:
            params["bcc"] = bcc

        # If live API key is present and valid (not a test dummy key)
        if HAS_RESEND_LIB and self.is_configured() and not self.api_key.startswith("re_test_") and not self.api_key.startswith("re_mock_"):
            try:
                resend.api_key = self.api_key
                response = resend.Emails.send(params)
                return {
                    "id": response.get("id", f"resend_{uuid.uuid4().hex[:12]}"),
                    "from": sender,
                    "to": recipients,
                    "subject": subject,
                    "status": "sent",
                    "mode": "live",
                }
            except Exception as ex:
                raise RuntimeError(f"Resend API Error: {str(ex)}") from ex

        # Mock / Simulation Fallback
        mock_id = f"re_mock_{uuid.uuid4().hex[:16]}"
        return {
            "id": mock_id,
            "from": sender,
            "to": recipients,
            "subject": subject,
            "status": "sent",
            "mode": "mock",
            "message": "Simulated live email dispatch via Resend Mock engine.",
        }
