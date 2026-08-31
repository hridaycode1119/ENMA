"""
End-to-End Workflow & Orchestration Tests for the Streamlit Application Core.
"""

import unittest
from agent.orchestrator import AgentOrchestrator, WorkflowState

class TestAppFlow(unittest.TestCase):

    def setUp(self):
        self.orchestrator = AgentOrchestrator()

    def test_complete_happy_path_flow(self):
        # 1. Initial State
        self.assertEqual(self.orchestrator.state, WorkflowState.IDLE)
        self.assertIsNone(self.orchestrator.current_plan)

        # 2. Ingest explicit task
        plan = self.orchestrator.submit_instruction(
            "Send an email to dr.sharma@university.edu informing him that our BTech Major Project Phase 1 is complete."
        )
        self.assertEqual(self.orchestrator.state, WorkflowState.AWAITING_APPROVAL)
        self.assertFalse(plan.requires_clarification)
        self.assertEqual(plan.tool_parameters["recipient_email"], "dr.sharma@university.edu")

        # 3. Simulate User editing subject in Draft Card
        modified_params = dict(plan.tool_parameters)
        modified_params["subject"] = "Final Phase 1 Report - BTech Major Project"

        # 4. User approves and executes
        result = self.orchestrator.execute_confirmed_task(override_parameters=modified_params)
        self.assertTrue(result.success)
        self.assertEqual(self.orchestrator.state, WorkflowState.COMPLETED)
        self.assertIsNotNone(result.external_reference_id)
        self.assertEqual(result.data["subject"], "Final Phase 1 Report - BTech Major Project")
        self.assertEqual(len(self.orchestrator.history), 1)

        # 5. Reset back to IDLE
        self.orchestrator.reset()
        self.assertEqual(self.orchestrator.state, WorkflowState.IDLE)
        self.assertIsNone(self.orchestrator.current_plan)

    def test_clarification_and_resolution_flow(self):
        # 1. Ingest ambiguous task missing recipient email
        plan = self.orchestrator.submit_instruction(
            "Send an email to my project partner asking for the code repo link."
        )
        self.assertEqual(self.orchestrator.state, WorkflowState.CLARIFICATION_REQUIRED)
        self.assertTrue(plan.requires_clarification)

        # 2. Provide missing email
        resolved_plan = self.orchestrator.submit_clarification({"recipient_email": "partner@univ.edu"})
        self.assertEqual(self.orchestrator.state, WorkflowState.AWAITING_APPROVAL)
        self.assertFalse(resolved_plan.requires_clarification)
        self.assertEqual(resolved_plan.tool_parameters["recipient_email"], "partner@univ.edu")

        # 3. Execute approved task
        result = self.orchestrator.execute_confirmed_task()
        self.assertTrue(result.success)
        self.assertEqual(self.orchestrator.state, WorkflowState.COMPLETED)

    def test_task_cancellation(self):
        self.orchestrator.submit_instruction("Send an email to client@corp.com with monthly invoice.")
        self.assertEqual(self.orchestrator.state, WorkflowState.AWAITING_APPROVAL)

        # User cancels
        self.orchestrator.cancel_current_task()
        self.assertEqual(self.orchestrator.state, WorkflowState.CANCELLED)
        self.assertIsNone(self.orchestrator.current_plan)
        self.assertEqual(len(self.orchestrator.history), 1)
        self.assertEqual(self.orchestrator.history[0]["status"], "CANCELLED")

if __name__ == "__main__":
    unittest.main()
