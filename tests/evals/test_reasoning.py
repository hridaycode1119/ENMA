"""
Benchmark Cognitive Reasoning and Evaluation Test Suite.
Tests the agent's intent extraction, parameter validation,
ambiguity detection, and security guardrails across benchmark cases.
"""

import json
import os
import unittest
from agent.parser import IntentParser
from schemas.task_schemas import TaskType

class TestCognitiveReasoningBenchmarks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = IntentParser()
        dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            cls.dataset = json.load(f)

    def test_benchmark_suite_accuracy(self):
        total_cases = len(self.dataset)
        passed_cases = 0
        failures = []

        for case in self.dataset:
            case_id = case["id"]
            prompt = case["prompt"]
            expected_type = case["expected_task_type"]
            expected_clarify = case["expected_clarification"]

            try:
                plan = self.parser.parse_instruction(prompt)

                # Assert Task Type
                self.assertEqual(
                    plan.task_type.value,
                    expected_type,
                    f"[{case_id}] Expected task_type {expected_type}, got {plan.task_type.value}",
                )

                # Assert Clarification Flag
                self.assertEqual(
                    plan.requires_clarification,
                    expected_clarify,
                    f"[{case_id}] Expected requires_clarification={expected_clarify}, got {plan.requires_clarification}",
                )

                # If explicit recipient expected, verify extraction
                if "expected_recipient" in case:
                    self.assertIn("recipient_email", plan.tool_parameters)
                    self.assertEqual(
                        plan.tool_parameters["recipient_email"],
                        case["expected_recipient"],
                        f"[{case_id}] Expected recipient {case['expected_recipient']}",
                    )

                # If missing field expected, verify in clarification
                if "expected_missing_field" in case:
                    self.assertIsNotNone(plan.clarification)
                    self.assertIn(
                        case["expected_missing_field"],
                        plan.clarification.missing_fields,
                    )

                # If tone expected, verify
                if "expected_tone" in case:
                    self.assertEqual(
                        plan.tool_parameters.get("tone"),
                        case["expected_tone"],
                    )

                passed_cases += 1
            except Exception as ex:
                failures.append(f"{case_id}: {str(ex)}")

        accuracy = (passed_cases / total_cases) * 100
        print(f"\n=======================================================")
        print(f" 📊 COGNITIVE REASONING EVALUATION RESULTS:")
        print(f" Total Test Cases : {total_cases}")
        print(f" Passed Cases     : {passed_cases}")
        print(f" Accuracy Rate    : {accuracy:.1f}% (Threshold: >= 95.0%)")
        print(f"=======================================================")

        if failures:
            print("\nFailures:\n" + "\n".join(failures))

        self.assertGreaterEqual(
            accuracy,
            95.0,
            f"Cognitive reasoning accuracy {accuracy:.1f}% fell below the 95.0% threshold.",
        )

    def test_dynamic_clarification_resolution(self):
        """Tests that providing a missing email turns an ambiguous plan into a valid ready-to-execute plan."""
        incomplete_prompt = "Send an email to my project guide asking for the review slot."
        plan = self.parser.parse_instruction(incomplete_prompt)

        self.assertTrue(plan.requires_clarification)
        self.assertIsNotNone(plan.clarification)
        self.assertIn("recipient_email", plan.clarification.missing_fields)

        # Resolve clarification
        resolved_plan = self.parser.resolve_clarification(
            plan,
            {"recipient_email": "guide.prof@university.edu"}
        )

        self.assertFalse(resolved_plan.requires_clarification)
        self.assertIsNone(resolved_plan.clarification)
        self.assertEqual(
            resolved_plan.tool_parameters["recipient_email"],
            "guide.prof@university.edu",
        )

        email_payload = resolved_plan.get_email_payload()
        self.assertIsNotNone(email_payload)
        self.assertEqual(email_payload.recipient_email, "guide.prof@university.edu")

if __name__ == "__main__":
    unittest.main()
