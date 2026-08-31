"""
Unit tests for data schemas and validation models.
"""

import unittest
from schemas.task_schemas import (
    TaskType,
    EmailTone,
    EmailPriority,
    EmailDraftPayload,
    ClarificationRequest,
    TaskPlan,
    AgentDecision,
)

class TestTaskSchemas(unittest.TestCase):

    def test_valid_email_draft_payload(self):
        payload = EmailDraftPayload(
            recipient_email="advisor@university.edu",
            recipient_name="Dr. Advisor",
            subject="Project Phase 1 Review",
            body_text="Dear Dr. Advisor, we have completed Phase 1.",
            tone=EmailTone.FORMAL,
            priority=EmailPriority.NORMAL,
        )
        self.assertEqual(payload.recipient_email, "advisor@university.edu")
        self.assertEqual(payload.recipient_name, "Dr. Advisor")
        self.assertEqual(payload.tone, EmailTone.FORMAL)
        self.assertEqual(payload.priority, EmailPriority.NORMAL)
        self.assertIn("<p>", payload.body_html)

        d = payload.to_dict()
        self.assertEqual(d["recipient_email"], "advisor@university.edu")
        rebuilt = EmailDraftPayload.from_dict(d)
        self.assertEqual(rebuilt.subject, payload.subject)

    def test_invalid_email_format(self):
        with self.assertRaises(ValueError):
            EmailDraftPayload(
                recipient_email="invalid-email-address",
                subject="Test Subject",
                body_text="Valid body text here.",
            )

        with self.assertRaises(ValueError):
            EmailDraftPayload(
                recipient_email="",
                subject="Test Subject",
                body_text="Valid body text here.",
            )

    def test_short_subject_and_body_validation(self):
        with self.assertRaises(ValueError):
            EmailDraftPayload(
                recipient_email="user@example.com",
                subject="a",
                body_text="Valid body text here.",
            )

        with self.assertRaises(ValueError):
            EmailDraftPayload(
                recipient_email="user@example.com",
                subject="Valid Subject",
                body_text="Hi",
            )

    def test_tone_and_priority_enums(self):
        self.assertEqual(EmailTone.from_str("FORMAL"), EmailTone.FORMAL)
        self.assertEqual(EmailTone.from_str("casual"), EmailTone.CASUAL)
        self.assertEqual(EmailTone.from_str("unknown_tone"), EmailTone.PROFESSIONAL)

        self.assertEqual(EmailPriority.from_str("HIGH"), EmailPriority.HIGH)
        self.assertEqual(EmailPriority.from_str("low"), EmailPriority.LOW)
        self.assertEqual(EmailPriority.from_str("unknown"), EmailPriority.NORMAL)

    def test_clarification_request_serialization(self):
        req = ClarificationRequest(
            missing_fields=["recipient_email"],
            question_for_user="Who should receive this email?",
            suggested_defaults={"tone": "professional"},
        )
        d = req.to_dict()
        self.assertEqual(d["missing_fields"], ["recipient_email"])
        self.assertEqual(d["question_for_user"], "Who should receive this email?")

        reconstructed = ClarificationRequest.from_dict(d)
        self.assertEqual(reconstructed.missing_fields, ["recipient_email"])

    def test_task_plan_serialization_and_deserialization(self):
        plan = TaskPlan(
            task_type=TaskType.EMAIL_SEND,
            intent_summary="Send project update",
            confidence=0.95,
            requires_clarification=False,
            target_tool="gmail_send_tool",
            tool_parameters={
                "recipient_email": "test@domain.com",
                "subject": "Status Report",
                "body_text": "Here is the status report for today.",
            },
        )
        json_str = plan.to_json()
        self.assertIn("EMAIL_SEND", json_str)
        self.assertIn("test@domain.com", json_str)

        loaded_plan = TaskPlan.from_json(json_str)
        self.assertEqual(loaded_plan.task_type, TaskType.EMAIL_SEND)
        self.assertEqual(loaded_plan.confidence, 0.95)
        
        email_payload = loaded_plan.get_email_payload()
        self.assertIsNotNone(email_payload)
        self.assertEqual(email_payload.recipient_email, "test@domain.com")

    def test_agent_decision(self):
        plan = TaskPlan(
            task_type=TaskType.EMAIL_SEND,
            intent_summary="Quick note",
            tool_parameters={
                "recipient_email": "hello@world.com",
                "subject": "Quick Note",
                "body_text": "Just checking in on the task.",
            },
        )
        decision = AgentDecision(task_plan=plan, raw_reasoning="Intent is clear.")
        d = decision.to_dict()
        self.assertEqual(d["raw_reasoning"], "Intent is clear.")

        dec_from_dict = AgentDecision.from_dict(d)
        self.assertEqual(dec_from_dict.task_plan.task_type, TaskType.EMAIL_SEND)

if __name__ == "__main__":
    unittest.main()
