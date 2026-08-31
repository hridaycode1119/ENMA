#!/usr/bin/env python3
"""
Interactive CLI Test Harness for Autonomous AI Agent Reasoning.
Allows developers and evaluators to test natural language parsing,
parameter extraction, tone modulation, and clarification loops in real time.
"""

import os
import sys
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.parser import IntentParser
from agent.llm_adapter import MockLLMAdapter, LLMAdapter

def print_banner():
    print("=" * 75)
    print(" 🤖  AUTONOMOUS AI AGENT - REASONING & INTENT PARSER CLI  🤖 ")
    print("=" * 75)
    print("Type your natural language enterprise instruction below.")
    print("Type 'exit' or 'quit' to exit.")
    print("-" * 75)

def main():
    print_banner()
    parser = IntentParser()

    while True:
        try:
            user_input = input("\n📝 Enter Instruction > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("\n👋 Exiting test harness. Goodbye!")
                break

            print("\n⚙️  Processing with Agent Reasoning Engine...")
            plan = parser.parse_instruction(user_input)

            print("\n" + "=" * 50)
            print("  📋 SYNTHESIZED TASK PLAN OUTPUT")
            print("=" * 50)
            print(f"• Task ID        : {plan.task_id}")
            print(f"• Task Type      : {plan.task_type.value}")
            print(f"• Confidence     : {plan.confidence * 100:.1f}%")
            print(f"• Target Tool    : {plan.target_tool}")
            print(f"• Clarify Needed : {'YES ⚠️' if plan.requires_clarification else 'NO ✅'}")

            if plan.requires_clarification and plan.clarification:
                print(f"\n❓ Clarification Question:")
                print(f"   \"{plan.clarification.question_for_user}\"")
                print(f"   Missing Fields: {plan.clarification.missing_fields}")

                # Optional interactive clarification prompt
                provide_now = input("\n👉 Would you like to provide the missing field now? (y/n): ").strip().lower()
                if provide_now == 'y':
                    answers = {}
                    for field in plan.clarification.missing_fields:
                        val = input(f"   Enter {field}: ").strip()
                        answers[field] = val
                    plan = parser.resolve_clarification(plan, answers)
                    print("\n✅ Clarification Resolved! Updated Plan:")

            if not plan.requires_clarification:
                payload = plan.get_email_payload()
                if payload:
                    print("\n✉️  GENERATED EMAIL DRAFT:")
                    print(f"   To      : {payload.recipient_email} ({payload.recipient_name or 'N/A'})")
                    print(f"   Subject : {payload.subject}")
                    print(f"   Tone    : {payload.tone.value.upper()} | Priority: {payload.priority.value.upper()}")
                    print("   " + "-" * 45)
                    for line in payload.body_text.split("\n"):
                        print(f"   {line}")
                    print("   " + "-" * 45)

            print("\n📄 Raw JSON Output:")
            print(plan.to_json(indent=2))

        except KeyboardInterrupt:
            print("\n\nOperation cancelled. Exiting.")
            break
        except Exception as ex:
            print(f"\n❌ Error: {str(ex)}")

if __name__ == "__main__":
    main()
