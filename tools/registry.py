"""
Dynamic Tool Registry & Execution Dispatcher.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from security.action_guard import ActionGuard
from .base import BaseTool, ToolMetadata, ToolResult, ToolSafetyLevel
from .gmail.gmail_tool import GmailDraftTool, GmailSendTool
from .documents.document_tools import DocumentAnalyzeTool, DocumentEditTool, DocumentConvertTool
from .calendar.calendar_tool import CalendarScheduleTool

class ToolRegistry:
    """
    Central dynamic registry managing tool discovery, schema exports, and execution gates.
    """

    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, BaseTool] = {}

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._tools = {}
            cls._register_defaults()
        return cls._instance

    @classmethod
    def _register_defaults(cls) -> None:
        """Registers default built-in tools."""
        cls.register(GmailSendTool())
        cls.register(GmailDraftTool())
        cls.register(DocumentAnalyzeTool())
        cls.register(DocumentEditTool())
        cls.register(DocumentConvertTool())
        cls.register(CalendarScheduleTool())

    @classmethod
    def register(cls, tool: BaseTool) -> BaseTool:
        """Registers a new tool instance in the registry."""
        meta = tool.metadata
        cls._tools[meta.name] = tool
        return tool

    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        """Retrieves tool instance by name."""
        if not cls._tools:
            cls._register_defaults()
        return cls._tools.get(name.strip())

    @classmethod
    def list_tools(cls) -> List[ToolMetadata]:
        """Lists metadata descriptors for all registered tools."""
        if not cls._tools:
            cls._register_defaults()
        return [tool.metadata for tool in cls._tools.values()]

    @classmethod
    def list_tool_names(cls) -> List[str]:
        """Returns list of registered tool names."""
        if not cls._tools:
            cls._register_defaults()
        return list(cls._tools.keys())

    @classmethod
    def execute_tool(
        cls,
        tool_name: str,
        parameters: Dict[str, Any],
        user_confirmed: bool = False,
    ) -> ToolResult:
        """
        Validates safety constraints, checks human-in-the-loop authorization,
        and executes target tool.
        """
        tool = cls.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error_message=f"Tool '{tool_name}' is not registered in the tool system.",
            )

        # 1. Safety Guard Check
        try:
            ActionGuard.verify_execution(
                tool_name=tool_name,
                safety_level=tool.metadata.safety_level.value,
                user_confirmed=user_confirmed,
            )
        except PermissionError as perm_err:
            return ToolResult(
                success=False,
                error_message=str(perm_err),
            )

        # 2. Parameter Validation & Execution
        try:
            validated = tool.validate_parameters(parameters)
            return tool.execute(validated)
        except Exception as ex:
            return ToolResult(
                success=False,
                error_message=f"Parameter validation failed: {str(ex)}",
            )
