"""
Master Agent Orchestrator & State Transition Coordinator.
Coordinates between UI session states, Intent Parser, Safety Guards, and Tool Registries.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from enum import Enum

from schemas.task_schemas import EmailDraftPayload, TaskPlan, TaskType
from .parser import IntentParser
from tools.registry import ToolRegistry
from tools.base import ToolResult
from integrations.oauth_handler import GoogleOAuthHandler
from database.repository import AIRARepository

class WorkflowState(str, Enum):
    """Finite state machine states for the task automation lifecycle."""
    IDLE = "IDLE"
    PARSING = "PARSING"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class AgentOrchestrator:
    """
    Central Controller for the Autonomous AI Agent application.
    """

    def __init__(
        self,
        parser: Optional[IntentParser] = None,
        registry: Optional[ToolRegistry] = None,
        oauth_handler: Optional[GoogleOAuthHandler] = None,
    ):
        self.parser = parser or IntentParser()
        self.registry = registry or ToolRegistry()
        self.oauth = oauth_handler or GoogleOAuthHandler()
        self.current_plan: Optional[TaskPlan] = None
        self.state: WorkflowState = WorkflowState.IDLE
        self.history: List[Dict[str, Any]] = []
        self.last_result: Optional[ToolResult] = None
        self.last_execution_time_ms: float = 0.0

    def submit_instruction(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """
        Receives raw user instruction and transitions state to PARSING -> AWAITING_APPROVAL / CLARIFICATION.
        """
        self.state = WorkflowState.PARSING
        start_time = time.time()

        try:
            plan = self.parser.parse_instruction(instruction, context=context)
            self.current_plan = plan

            if plan.requires_clarification:
                self.state = WorkflowState.CLARIFICATION_REQUIRED
            elif plan.task_type == TaskType.UNKNOWN:
                self.state = WorkflowState.FAILED
                self.last_result = ToolResult(
                    success=False,
                    error_message="Instruction not supported or was rejected by safety filters.",
                )
            else:
                self.state = WorkflowState.AWAITING_APPROVAL

            self.last_execution_time_ms = (time.time() - start_time) * 1000
            return plan

        except Exception as ex:
            self.state = WorkflowState.FAILED
            self.last_result = ToolResult(success=False, error_message=str(ex))
            raise ex

    def submit_clarification(self, user_responses: Dict[str, Any]) -> TaskPlan:
        """
        Merges clarification inputs into pending plan.
        """
        if not self.current_plan:
            raise ValueError("No active task plan awaiting clarification.")

        plan = self.parser.resolve_clarification(self.current_plan, user_responses)
        self.current_plan = plan

        if not plan.requires_clarification:
            self.state = WorkflowState.AWAITING_APPROVAL
        else:
            self.state = WorkflowState.CLARIFICATION_REQUIRED

        return plan

    def execute_confirmed_task(
        self,
        override_parameters: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """
        Executes the human-reviewed plan through the tool registry with explicit user confirmation.
        """
        if not self.current_plan:
            return ToolResult(success=False, error_message="No active plan to execute.")

        self.state = WorkflowState.EXECUTING
        start_time = time.time()

        params = dict(override_parameters or self.current_plan.tool_parameters)

        # Update current plan parameters with any user modifications
        self.current_plan.tool_parameters = params

        # Execute through tool registry with user_confirmed=True
        result = self.registry.execute_tool(
            tool_name=self.current_plan.target_tool,
            parameters=params,
            user_confirmed=True,
        )

        self.last_result = result
        self.last_execution_time_ms = (time.time() - start_time) * 1000

        if result.success:
            self.state = WorkflowState.COMPLETED
            # Record in task history
            self._record_history_entry(status="COMPLETED", ref_id=result.external_reference_id)
        else:
            self.state = WorkflowState.FAILED
            self._record_history_entry(status="FAILED", error=result.error_message)

        return result

    def cancel_current_task(self) -> None:
        """Aborts active task and resets state cleanly."""
        if self.current_plan:
            self._record_history_entry(status="CANCELLED")
        self.state = WorkflowState.CANCELLED
        self.current_plan = None

    def reset(self) -> None:
        """Resets orchestrator back to clean IDLE state."""
        self.state = WorkflowState.IDLE
        self.current_plan = None
        self.last_result = None

    def _record_history_entry(
        self,
        status: str,
        ref_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.current_plan:
            return
        entry = {
            "task_id": self.current_plan.task_id,
            "task_type": self.current_plan.task_type.value,
            "intent": self.current_plan.intent_summary,
            "target_tool": self.current_plan.target_tool,
            "status": status,
            "reference_id": ref_id,
            "error": error,
            "timestamp": time.time(),
        }
        self.history.insert(0, entry)

        # Sync to database repository
        try:
            AIRARepository().save_task(
                task_id=self.current_plan.task_id,
                user_instruction=self.current_plan.intent_summary or "Autonomous Task",
                state=status,
                plan_json=self.current_plan.tool_parameters,
                tool_name=self.current_plan.target_tool,
                execution_time_ms=self.last_execution_time_ms,
                error_message=error,
            )
        except Exception:
            pass
