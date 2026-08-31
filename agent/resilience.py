"""
Resilience, Exception Hierarchy and Retry Policies.
"""

from __future__ import annotations
import functools
import random
import time
from typing import Any, Callable, List, Optional, Type, Tuple

class AgentBaseException(Exception):
    """Root application exception with user-facing message and traceability."""
    def __init__(
        self,
        message: str,
        user_message: str = "An unexpected error occurred while processing your task.",
        error_code: str = "ERR_INTERNAL",
        recoverable: bool = True,
    ):
        super().__init__(message)
        self.message = message
        self.user_message = user_message
        self.error_code = error_code
        self.recoverable = recoverable

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "recoverable": self.recoverable,
        }

class ParameterValidationError(AgentBaseException):
    """Raised when extracted parameters fail schema or semantic validation."""
    def __init__(self, message: str, missing_fields: Optional[List[str]] = None):
        super().__init__(
            message=message,
            user_message="Some required information is missing or formatted incorrectly.",
            error_code="ERR_PARAM_VALIDATION",
            recoverable=True,
        )
        self.missing_fields = missing_fields or []

class LLMReasoningError(AgentBaseException):
    """Raised when LLM returns invalid JSON or fails to produce a viable plan."""
    def __init__(self, message: str, raw_output: Optional[str] = None):
        super().__init__(
            message=message,
            user_message="The AI engine could not synthesize a valid plan for this instruction.",
            error_code="ERR_LLM_REASONING",
            recoverable=True,
        )
        self.raw_output = raw_output

class AuthenticationError(AgentBaseException):
    """Raised when Google OAuth2 or API token authentication fails."""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            user_message="Authentication failed. Please verify your credentials or reconnect your account.",
            error_code="ERR_AUTH_FAILURE",
            recoverable=True,
        )

class ToolExecutionError(AgentBaseException):
    """Raised when an external tool or API call encounters an execution failure."""
    def __init__(self, message: str, tool_name: str, status_code: Optional[int] = None):
        super().__init__(
            message=message,
            user_message=f"Failed to complete the requested action on {tool_name}.",
            error_code="ERR_TOOL_EXECUTION",
            recoverable=True,
        )
        self.tool_name = tool_name
        self.status_code = status_code


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator implementing exponential backoff with jitter for resilient API calls.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as exc:
                    last_exception = exc
                    if attempt == max_retries:
                        break
                    
                    sleep_time = delay * (backoff_factor ** (attempt - 1))
                    if jitter:
                        sleep_time += random.uniform(0.1, 0.5)
                    
                    time.sleep(sleep_time)

            if last_exception:
                raise last_exception
        return wrapper
    return decorator
