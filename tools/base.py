"""
Base Tool Abstractions and Interface Specifications.
"""

from __future__ import annotations
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

class ToolSafetyLevel(str, Enum):
    """Safety classification determining whether human confirmation is required."""
    READ_ONLY = "read_only"         # Safe for automated execution (e.g. search, read profile)
    WRITE_SAFE = "write_safe"       # Non-destructive / reversible write (e.g. saving draft)
    CONSEQUENTIAL = "consequential" # Consequential / external mutation (e.g. sending email, deleting)

class ToolMetadata:
    """Descriptor metadata for registered tools."""

    def __init__(
        self,
        name: str,
        display_name: str,
        description: str,
        safety_level: ToolSafetyLevel | str = ToolSafetyLevel.CONSEQUENTIAL,
        version: str = "1.0.0",
    ):
        self.name = name.strip()
        self.display_name = display_name.strip()
        self.description = description.strip()
        self.safety_level = (
            safety_level
            if isinstance(safety_level, ToolSafetyLevel)
            else ToolSafetyLevel(str(safety_level).lower())
        )
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "safety_level": self.safety_level.value,
            "version": self.version,
        }

class ToolResult:
    """Standardized output returned by every tool execution."""

    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        external_reference_id: Optional[str] = None,
        execution_time_ms: float = 0.0,
    ):
        self.success = bool(success)
        self.data = data or {}
        self.error_message = error_message
        self.external_reference_id = external_reference_id
        self.execution_time_ms = float(execution_time_ms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error_message": self.error_message,
            "external_reference_id": self.external_reference_id,
            "execution_time_ms": self.execution_time_ms,
        }

    def __repr__(self) -> str:
        return f"<ToolResult success={self.success} ref={self.external_reference_id} time={self.execution_time_ms:.1f}ms>"

class BaseTool(ABC):
    """Abstract Base Class for all tools in the Autonomous AI Agent ecosystem."""

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Returns tool metadata descriptor."""
        pass

    @abstractmethod
    def validate_parameters(self, params: Dict[str, Any]) -> Any:
        """Validates incoming dictionary parameters."""
        pass

    @abstractmethod
    def execute(self, validated_params: Any) -> ToolResult:
        """Executes the tool logic and returns a standardized ToolResult."""
        pass
