# Workflow & State Machine Specification
## Autonomous AI Agent for Enterprise Task Automation

**Document Version:** 1.0.0  
**Status:** Approved  
**Execution Model:** Deterministic Finite State Machine (FSM)  

---

## 1. End-to-End Workflow Sequences

### 1.1 Workflow 1: Standard Execution (Happy Path)

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant UI as Streamlit UI
    participant Agent as Agent Orchestrator
    participant LLM as Gemini LLM
    participant Guard as Action Safety Gate
    participant Tool as GmailSendTool
    participant DB as SQLite DB

    User->>UI: Types "Send project update to guide@univ.edu..."
    UI->>Agent: process_user_prompt(prompt)
    Agent->>DB: create_task(status='PARSING')
    Agent->>LLM: generate_task_plan(prompt, tool_schemas)
    LLM-->>Agent: TaskPlan JSON (No ambiguities)
    Agent->>DB: update_task(status='AWAITING_APPROVAL', draft=payload)
    Agent-->>UI: Display Editable Draft Card
    
    User->>UI: Edits subject & clicks "Approve & Send"
    UI->>Agent: execute_approved_task(task_id, modified_payload)
    Agent->>Guard: verify_action_permission('gmail_send_tool', confirmed=True)
    Guard-->>Agent: Action Permitted
    
    Agent->>DB: update_task(status='EXECUTING')
    Agent->>Tool: execute(modified_payload)
    Tool->>Tool: Send via Gmail REST API
    Tool-->>Agent: ToolResult(success=True, message_id='msg-99201')
    
    Agent->>DB: update_task(status='COMPLETED', external_id='msg-99201')
    Agent-->>UI: Display Success Confirmation & Message ID
```

---

### 1.2 Workflow 2: Ambiguous / Incomplete Parameter Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant UI as Streamlit UI
    participant Agent as Agent Orchestrator
    participant LLM as Gemini LLM

    User->>UI: Types "Email the team about our meeting tomorrow"
    UI->>Agent: process_user_prompt(prompt)
    Agent->>LLM: generate_task_plan(prompt)
    LLM-->>Agent: TaskPlan(requires_clarification=True, missing=['recipient_email'])
    Agent-->>UI: Render Clarification Input ("Please specify recipient email")
    User->>UI: Enters "team-leads@enterprise.com" & submits
    UI->>Agent: submit_clarification(task_id, {'recipient_email': 'team-leads@enterprise.com'})
    Agent->>LLM: re_evaluate_plan(combined_context)
    LLM-->>Agent: Valid TaskPlan
    Agent-->>UI: Present Draft Preview
```

---

### 1.3 Workflow 3: OAuth Token Refresh & Re-Authentication Flow

```mermaid
sequenceDiagram
    autonumber
    participant Tool as GmailSendTool
    participant Auth as GoogleOAuthHandler
    participant GoogleAuth as Google Token Endpoint
    participant User as User / Browser

    Tool->>Auth: get_valid_credentials()
    Auth->>Auth: Check token expiry
    alt Token is Valid
        Auth-->>Tool: Return Credentials
    else Token Expired but Refresh Token Present
        Auth->>GoogleAuth: POST /token (grant_type=refresh_token)
        GoogleAuth-->>Auth: New Access Token
        Auth->>Auth: Update local token cache
        Auth-->>Tool: Return Refreshed Credentials
    else No Valid Refresh Token
        Auth->>User: Open System Browser for Consent
        User->>GoogleAuth: Approve Scopes
        GoogleAuth-->>Auth: Exchange Code for Access/Refresh Tokens
        Auth->>Auth: Save encrypted credentials
        Auth-->>Tool: Return Valid Credentials
    end
```

---

## 2. State Transition Matrix

The table below enforces legal state transitions across the application lifecycle:

| Current State | Trigger Event | Guard Condition | Next State | Actions Executed |
|---|---|---|---|---|
| `IDLE` | `SUBMIT_PROMPT` | Prompt length $> 5$ chars | `PARSING` | Initialize `TaskRecord` in DB; record start timestamp. |
| `PARSING` | `PLAN_GENERATED` | Schema valid, no missing fields | `AWAITING_APPROVAL` | Save draft in DB; render interactive UI draft card. |
| `PARSING` | `MISSING_FIELDS` | Confidence $< 0.7$ or missing email | `CLARIFICATION` | Render question prompt in UI; pause execution. |
| `CLARIFICATION` | `SUBMIT_INFO` | Required fields provided | `PARSING` | Append info to prompt context; re-invoke LLM. |
| `AWAITING_APPROVAL` | `CLICK_APPROVE` | User confirms; payload valid | `EXECUTING` | Lock draft; check tool permissions; invoke tool. |
| `AWAITING_APPROVAL` | `CLICK_CANCEL` | User clicks cancel button | `CANCELLED` | Record cancellation in DB; clean UI state. |
| `EXECUTING` | `API_SUCCESS` | External API returns HTTP 200 | `COMPLETED` | Store external message ID; display success alert. |
| `EXECUTING` | `API_ERROR` | Retries exhausted / 4xx/5xx | `FAILED` | Capture error message; log audit failure; alert user. |
| `COMPLETED` / `FAILED` / `CANCELLED` | `RESET_TASK` | None | `IDLE` | Reset session state for new workflow. |

---

## 3. Workflow Telemetry & Metrics Hooks

Every state change triggers an asynchronous telemetry hook recording:
- `task_id`: UUID
- `from_state` $\rightarrow$ `to_state`
- `latency_ms`: Duration spent in previous state
- `metadata`: Tool name, retry count, token consumption (prompt/completion tokens)
