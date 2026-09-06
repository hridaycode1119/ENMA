"""
Universal LLM Adapter Interface for Google Gemini API and Offline Heuristic Reasoning.
"""

from __future__ import annotations
import json
import os
import re
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

def load_dotenv_if_present() -> None:
    """Lightweight .env file loader that reads key-value pairs into os.environ."""
    env_paths = [".env", os.path.join(os.path.dirname(__file__), "..", ".env")]
    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            # Strip optional quotes
                            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                                v = v[1:-1]
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

# Automatically load .env on module import
load_dotenv_if_present()

from schemas.task_schemas import (
    AgentDecision,
    ClarificationRequest,
    EmailPriority,
    EmailTone,
    TaskPlan,
    TaskType,
)
from .resilience import LLMReasoningError, retry_with_backoff

class BaseLLMAdapter(ABC):
    """Abstract interface for LLM reasoning engines."""

    @abstractmethod
    def generate_decision(self, prompt: str, user_instruction: str) -> AgentDecision:
        """Executes reasoning and returns structured AgentDecision."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generates raw text response for arbitrary prompting."""
        pass

class MockLLMAdapter(BaseLLMAdapter):
    """
    Deterministic cognitive reasoning engine for offline development,
    continuous integration testing, and instant evaluations without API keys.
    """

    EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
    INJECTION_KEYWORDS = ["ignore previous", "dump database", "drop table", "override rules", "bypass"]
    URGENT_KEYWORDS = ["urgent", "asap", "emergency", "immediately", "critical", "outage"]
    FORMAL_KEYWORDS = ["formal", "resignation", "leave", "permission", "dean", "professor", "dr.", "sir"]
    CASUAL_KEYWORDS = ["hey", "quick check", "casual", "partner", "bro", "catch up"]

    def generate_decision(self, prompt: str, user_instruction: str) -> AgentDecision:
        lowered = user_instruction.lower().strip()

        # 1. Prompt Injection / Malicious Instruction Defense
        if any(keyword in lowered for keyword in self.INJECTION_KEYWORDS):
            return AgentDecision(
                task_plan=TaskPlan(
                    task_type=TaskType.UNKNOWN,
                    intent_summary="Security filter: Instruction rejected as unsafe.",
                    confidence=1.0,
                    requires_clarification=False,
                    target_tool="none",
                    tool_parameters={},
                ),
                raw_reasoning="Harmful or adversarial keyword sequence detected.",
            )

        # 2. Unsupported task check
        unsupported_terms = [
            "stock", "shares", "nasdaq", "bitcoin", "crypto", "trade",
            "flight", "hotel", "ticket", "delete database", "weather",
            "play music", "turn on light"
        ]
        has_email_context = any(w in lowered for w in ["email", "mail", "draft", "message", "@"])
        if any(w in lowered for w in unsupported_terms) and not has_email_context:
            return AgentDecision(
                task_plan=TaskPlan(
                    task_type=TaskType.UNKNOWN,
                    intent_summary="Requested enterprise domain action is currently unsupported.",
                    confidence=0.9,
                    requires_clarification=False,
                    target_tool="none",
                    tool_parameters={},
                ),
                raw_reasoning="Intent does not match supported tool capabilities.",
            )

        # 3. Email Automation Parsing
        found_emails = self.EMAIL_PATTERN.findall(user_instruction)
        is_draft_only = "draft" in lowered and "send" not in lowered

        # Determine Tone
        if any(w in lowered for w in self.URGENT_KEYWORDS):
            tone = EmailTone.URGENT
            priority = EmailPriority.HIGH
        elif any(w in lowered for w in self.FORMAL_KEYWORDS):
            tone = EmailTone.FORMAL
            priority = EmailPriority.NORMAL
        elif any(w in lowered for w in self.CASUAL_KEYWORDS):
            tone = EmailTone.CASUAL
            priority = EmailPriority.LOW
        else:
            tone = EmailTone.PROFESSIONAL
            priority = EmailPriority.NORMAL

        # Check for Missing Recipient Email
        if not found_emails:
            # Extract target entity descriptor if possible
            target_entity = "recipient"
            if "guide" in lowered:
                target_entity = "project guide"
            elif "partner" in lowered:
                target_entity = "project partner"
            elif "manager" in lowered or "boss" in lowered:
                target_entity = "manager"
            elif "team" in lowered:
                target_entity = "team"
            elif "client" in lowered:
                target_entity = "client"

            return AgentDecision(
                task_plan=TaskPlan(
                    task_type=TaskType.EMAIL_DRAFT if is_draft_only else TaskType.EMAIL_SEND,
                    intent_summary=f"Prepare communication for {target_entity}",
                    confidence=0.75,
                    requires_clarification=True,
                    clarification=ClarificationRequest(
                        missing_fields=["recipient_email"],
                        question_for_user=f"Please specify the email address of your {target_entity} to proceed.",
                    ),
                    target_tool="gmail_draft_tool" if is_draft_only else "gmail_send_tool",
                    tool_parameters={
                        "recipient_name": target_entity.title(),
                        "subject": self._synthesize_subject(user_instruction),
                        "body_text": self._synthesize_body(user_instruction, target_entity, tone),
                        "tone": tone.value,
                        "priority": priority.value,
                    },
                ),
                raw_reasoning=f"Identified intent for {target_entity}, but recipient email is missing.",
            )

        # Explicit email address provided
        recipient_email = found_emails[0]
        recipient_name = recipient_email.split("@")[0].replace(".", " ").title()

        subject = self._synthesize_subject(user_instruction)
        body = self._synthesize_body(user_instruction, recipient_name, tone)

        return AgentDecision(
            task_plan=TaskPlan(
                task_type=TaskType.EMAIL_DRAFT if is_draft_only else TaskType.EMAIL_SEND,
                intent_summary=f"Automated email dispatch to {recipient_email}",
                confidence=0.98,
                requires_clarification=False,
                clarification=None,
                target_tool="gmail_draft_tool" if is_draft_only else "gmail_send_tool",
                tool_parameters={
                    "recipient_email": recipient_email,
                    "recipient_name": recipient_name,
                    "subject": subject,
                    "body_text": body,
                    "tone": tone.value,
                    "priority": priority.value,
                },
            ),
            raw_reasoning="Full recipient parameter and structured context extracted successfully.",
        )

    def _synthesize_subject(self, text: str) -> str:
        lowered = text.lower()
        if "phase 1" in lowered or "project" in lowered:
            return "Project Progress & Status Update"
        if "review" in lowered or "feedback" in lowered:
            return "Review Request & Project Feedback"
        if "leave" in lowered or "absence" in lowered:
            return "Formal Leave Application"
        if "server" in lowered or "down" in lowered or "outage" in lowered:
            return "URGENT: Service Outage Incident Report"
        if "invoice" in lowered:
            return "Invoice & Payment Follow-up"
        return "Update Regarding Enterprise Task"

    def _synthesize_body(self, text: str, name: str, tone: EmailTone) -> str:
        salutation = f"Dear {name}," if tone in (EmailTone.FORMAL, EmailTone.PROFESSIONAL) else f"Hi {name},"
        signoff = "Sincerely,\nProject Team" if tone == EmailTone.FORMAL else "Best regards,\nProject Team"
        
        # Clean user message core
        clean_msg = text
        for prefix in ["send an email to", "email to", "send email to", "write an email to", "draft an email to"]:
            if clean_msg.lower().startswith(prefix):
                clean_msg = clean_msg[len(prefix):].strip()
        
        body_content = f"I am writing to communicate the following update regarding our workflow:\n\n{clean_msg}"
        return f"{salutation}\n\n{body_content}\n\nPlease let us know if you need any additional information.\n\n{signoff}"

    def generate_text(self, prompt: str) -> str:
        """Offline fallback text generator."""
        return ""

class GeminiLLMAdapter(BaseLLMAdapter):
    """
    Production adapter interfacing with Google Gemini 1.5 API using strict JSON formatting.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.2,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.temperature = temperature

    @retry_with_backoff(max_retries=3, initial_delay=1.5, backoff_factor=2.0)
    def generate_decision(self, prompt: str, user_instruction: str) -> AgentDecision:
        if not self.api_key:
            # Gracefully delegate to mock adapter if API key is not configured
            return MockLLMAdapter().generate_decision(prompt, user_instruction)

        endpoint_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "responseMimeType": "application/json",
                "maxOutputTokens": 2048,
            },
        }

        req = urllib.request.Request(
            endpoint_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if not candidates:
                    raise LLMReasoningError("No response candidates returned by Gemini API.")

                raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                cleaned_text = self._clean_json_output(raw_text)
                decision_dict = json.loads(cleaned_text)
                return AgentDecision.from_dict(decision_dict)
        except urllib.error.HTTPError as http_err:
            if http_err.code == 429:
                raise LLMReasoningError("Gemini API rate limit exceeded (HTTP 429).")
            raise LLMReasoningError(f"Gemini API HTTP error {http_err.code}: {http_err.reason}")
        except json.JSONDecodeError as json_err:
            raise LLMReasoningError(f"Failed to parse LLM JSON output: {str(json_err)}")
        except Exception as ex:
            raise LLMReasoningError(f"Unexpected error communicating with Gemini API: {str(ex)}")

    def generate_text(self, prompt: str) -> str:
        """Offline fallback text generation."""
        return ""

    @staticmethod
    def _clean_json_output(raw_output: str) -> str:
        """Strips markdown ```json and ``` ticks if emitted."""
        text = raw_output.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def generate_text(self, prompt: str) -> str:
        """Generates raw text response using Google Gemini 1.5 API."""
        if not self.api_key:
            return ""

        endpoint_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 2048,
            },
        }

        req = urllib.request.Request(
            endpoint_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if candidates:
                    return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        except Exception:
            pass
        return ""

class LLMAdapter:
    """
    Factory creating either a Gemini API Adapter or Mock Adapter based on environment configuration.
    """

    @staticmethod
    def create(api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash") -> BaseLLMAdapter:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if key and key.strip() and key != "your_gemini_api_key_here":
            return GeminiLLMAdapter(api_key=key, model_name=model_name)
        return MockLLMAdapter()
