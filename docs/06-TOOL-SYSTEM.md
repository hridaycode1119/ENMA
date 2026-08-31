# Tool System & Dynamic Registry Specification
## Autonomous AI Agent for Enterprise Task Automation

**Document Version:** 1.0.0  
**Status:** Approved  
**Pattern:** Strategy Pattern + Dynamic Service Locator  

---

## 1. Overview & Architecture

The **Tool System** provides a standardized, decoupled interface allowing the agent's cognitive core to interact with external enterprise environments. Rather than hard-coding API integrations into the agent reasoning logic, all external capabilities are registered as modular tools.

```mermaid
graph TD
    subgraph Agent Core
        AgentOrchestrator[Agent Orchestrator]
    end

    subgraph Tool Infrastructure
        ToolRegistry[(Dynamic Tool Registry)]
        BaseTool[<<Abstract>> BaseTool]
        SafetyGate{Safety Gate HITL Check}
    end

    subgraph Registered Tools
        GmailSendTool[GmailSendTool - WRITE / CONSEQUENTIAL]
        GmailDraftTool[GmailDraftTool - WRITE / SAFE]
        DocGenTool[DocGenTool - WRITE / SAFE]
        CalScheduleTool[CalendarScheduleTool - WRITE / CONSEQUENTIAL]
    end

    AgentOrchestrator -->|Query Available Capabilities| ToolRegistry
    ToolRegistry --> BaseTool
    BaseTool <|-- GmailSendTool
    BaseTool <|-- GmailDraftTool
    BaseTool <|-- DocGenTool
    BaseTool <|-- CalScheduleTool

    AgentOrchestrator -->|Request Execution| SafetyGate
    SafetyGate -->|Approved| ToolRegistry
    ToolRegistry -->|Dispatch Params| GmailSendTool
```

---

## 2. Base Tool Contract (`BaseTool`)

Every tool in the system implements the abstract interface defined in `tools/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel
from enum import Enum

class ToolSafetyLevel(str, Enum):
    READ_ONLY = "read_only"       # Safe for automatic execution (e.g. search, fetch profile)
    WRITE_SAFE = "write_safe"     # Creates reversible draft/temp file
    CONSEQUENTIAL = "consequential" # Mutates external state (e.g. sending email, deleting file)

class ToolMetadata(BaseModel):
    name: str
    display_name: str
    description: str
    version: str = "1.0.0"
    safety_level: ToolSafetyLevel
    parameter_schema: Type[BaseModel]

class ToolResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    external_reference_id: Optional[str] = None

class BaseTool(ABC):
    """Abstract Base Class for all tools."""

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Returns the static metadata and schema of the tool."""
        pass

    @abstractmethod
    def validate(self, parameters: Dict[str, Any]) -> BaseModel:
        """Validates raw dictionary parameters against the tool's Pydantic schema."""
        pass

    @abstractmethod
    def execute(self, validated_params: BaseModel) -> ToolResult:
        """Executes the tool logic and returns a standardized ToolResult."""
        pass
```

---

## 3. Dynamic Tool Registry (`ToolRegistry`)

The `ToolRegistry` is a thread-safe singleton that manages tool discovery, capability exports, and dispatching:

```python
from typing import Dict, List, Optional
from loguru import logger

class ToolRegistry:
    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, BaseTool] = {}

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._tools = {}
        return cls._instance

    @classmethod
    def register(cls, tool_instance: BaseTool) -> BaseTool:
        name = tool_instance.metadata.name
        if name in cls._tools:
            logger.warning(f"Overwriting existing tool: {name}")
        cls._tools[name] = tool_instance
        logger.info(f"Registered tool: {name} [{tool_instance.metadata.safety_level}]")
        return tool_instance

    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[ToolMetadata]:
        return [tool.metadata for tool in cls._tools.values()]

    @classmethod
    def get_llm_tool_definitions(cls) -> List[Dict[str, Any]]:
        """Generates OpenAI / Gemini function calling tool schema definitions."""
        definitions = []
        for tool in cls._tools.values():
            meta = tool.metadata
            definitions.append({
                "name": meta.name,
                "description": meta.description,
                "parameters": meta.parameter_schema.model_json_schema()
            })
        return definitions
```

---

## 4. MVP Concrete Implementation: `GmailSendTool`

```python
import time
from tools.base import BaseTool, ToolMetadata, ToolSafetyLevel, ToolResult
from schemas.task_schemas import EmailDraftPayload
from integrations.gmail_client import GmailClient
from loguru import logger

class GmailSendTool(BaseTool):
    def __init__(self, client: Optional[GmailClient] = None):
        self.client = client or GmailClient()

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="gmail_send_tool",
            display_name="Gmail Dispatch Tool",
            description="Sends an email message to a specified recipient via the Gmail REST API.",
            safety_level=ToolSafetyLevel.CONSEQUENTIAL,
            parameter_schema=EmailDraftPayload
        )

    def validate(self, parameters: Dict[str, Any]) -> EmailDraftPayload:
        return EmailDraftPayload(**parameters)

    def execute(self, validated_params: EmailDraftPayload) -> ToolResult:
        start_time = time.time()
        try:
            logger.info(f"Executing Gmail dispatch to {validated_params.recipient_email}")
            response = self.client.send_email(
                to=validated_params.recipient_email,
                subject=validated_params.subject,
                body_text=validated_params.body_text,
                body_html=validated_params.body_html
            )
            elapsed = (time.time() - start_time) * 1000
            return ToolResult(
                success=True,
                data={"message_id": response["id"], "thread_id": response.get("threadId")},
                external_reference_id=response["id"],
                execution_time_ms=elapsed
            )
        except Exception as ex:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"GmailSendTool execution failed: {str(ex)}")
            return ToolResult(
                success=False,
                error_message=str(ex),
                execution_time_ms=elapsed
            )
```

---

## 5. Tool Safety Level Matrix

| Tool Name | Action Type | Safety Level | HITL Gate Required? | Reversible? |
|---|---|---|---|---|
| `gmail_send_tool` | Dispatches live email to recipient | `CONSEQUENTIAL` | **YES (Mandatory)** | No |
| `gmail_draft_tool` | Saves message to user's Drafts folder | `WRITE_SAFE` | Optional | Yes |
| `doc_generate_tool`| Creates local Word/PDF report | `WRITE_SAFE` | Optional | Yes |
| `calendar_schedule_tool` | Book event and notify attendees | `CONSEQUENTIAL` | **YES (Mandatory)** | Yes (via cancel) |
| `file_search_tool` | Queries local workspace documents | `READ_ONLY` | No (Auto-executed) | N/A |
