"""
Security & Consequential Action Guard.
Prevents unconfirmed real-world mutations (e.g., sending emails) without human confirmation.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

class ActionGuard:
    """
    Enforces Human-in-the-Loop (HITL) gatekeepers on consequential external actions.
    """

    @staticmethod
    def is_action_permitted(safety_level: str, user_confirmed: bool) -> bool:
        """
        Determines whether a tool action is permitted to execute based on its safety classification.
        - 'consequential': Requires explicit user_confirmed=True
        - 'write_safe': Reversible or draft write, permitted
        - 'read_only': Safe for automatic execution
        """
        level = str(safety_level).lower().strip()
        if level in ("consequential", "tool_safety_level.consequential"):
            return bool(user_confirmed)
        return True

    @classmethod
    def verify_execution(cls, tool_name: str, safety_level: str, user_confirmed: bool) -> None:
        """
        Raises a PermissionError if an action is blocked by the safety gate.
        """
        if not cls.is_action_permitted(safety_level, user_confirmed):
            raise PermissionError(
                f"Action blocked: Tool '{tool_name}' is classified as CONSEQUENTIAL and requires explicit human confirmation before execution."
            )
