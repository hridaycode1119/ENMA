"""
Intent Parser, Parameter Validation and Ambiguity Detection Engine.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from schemas.task_schemas import (
    ClarificationRequest,
    EmailDraftPayload,
    TaskPlan,
    TaskType,
)
from .llm_adapter import BaseLLMAdapter, LLMAdapter
from .prompts import build_agent_prompt
from .resilience import ParameterValidationError

class IntentParser:
    """
    Orchestrates natural language intent parsing, schema validation,
    ambiguity resolution, and clarification loops.
    """

    def __init__(self, adapter: Optional[BaseLLMAdapter] = None):
        self.adapter = adapter or LLMAdapter.create()

    def parse_instruction(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskPlan:
        """
        Processes free-form instruction into a validated TaskPlan.
        """
        if not instruction or not instruction.strip():
            raise ParameterValidationError("Instruction prompt cannot be empty.")

        cleaned_instruction = instruction.strip()
        prompt = build_agent_prompt(cleaned_instruction, context=context)

        # 1. Invoke reasoning adapter
        decision = self.adapter.generate_decision(prompt, cleaned_instruction)
        plan = decision.task_plan

        # 2. Post-parsing Validation & Safety Guard
        if plan.task_type in (TaskType.EMAIL_SEND, TaskType.EMAIL_DRAFT):
            params = plan.tool_parameters
            recipient = params.get("recipient_email")

            # Check if email is missing or empty
            if not recipient or not recipient.strip():
                plan.requires_clarification = True
                if not plan.clarification:
                    plan.clarification = ClarificationRequest(
                        missing_fields=["recipient_email"],
                        question_for_user="Please provide a valid recipient email address to proceed.",
                    )
            else:
                # Validate format
                try:
                    EmailDraftPayload._validate_email(recipient)
                except ValueError:
                    plan.requires_clarification = True
                    plan.clarification = ClarificationRequest(
                        missing_fields=["recipient_email"],
                        question_for_user=f"The email address '{recipient}' appears invalid. Please provide a valid email.",
                    )

        return plan

    def resolve_clarification(
        self,
        plan: TaskPlan,
        user_responses: Dict[str, Any],
    ) -> TaskPlan:
        """
        Merges user-provided clarification answers into an existing pending TaskPlan.
        """
        updated_params = dict(plan.tool_parameters)
        for key, value in user_responses.items():
            if value and str(value).strip():
                updated_params[key] = str(value).strip()

        # Check if all missing fields have been resolved
        missing_now = []
        if plan.clarification:
            for field in plan.clarification.missing_fields:
                if field not in updated_params or not updated_params[field]:
                    missing_now.append(field)

        if not missing_now:
            plan.requires_clarification = False
            plan.clarification = None
        else:
            plan.clarification.missing_fields = missing_now

        plan.tool_parameters = updated_params

        # Re-verify email payload if resolved
        if not plan.requires_clarification and plan.task_type in (TaskType.EMAIL_SEND, TaskType.EMAIL_DRAFT):
            try:
                EmailDraftPayload.from_dict(updated_params)
            except Exception as ex:
                raise ParameterValidationError(f"Invalid parameters after clarification: {str(ex)}")

        return plan
