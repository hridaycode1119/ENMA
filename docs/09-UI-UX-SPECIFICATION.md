# UI / UX Design & Frontend Specification
## Autonomous AI Agent for Enterprise Task Automation

**Document Version:** 1.0.0  
**Status:** Approved  
**Framework:** Streamlit 1.37+ with Custom Enterprise CSS  

---

## 1. User Interface Design Philosophy

The UI is engineered around three core tenets:
1. **Single-Pane Command Center:** Minimalist, zero-clutter interface focusing on conversational task dispatch and clear visual verification.
2. **Transparent Reasoning & Human Oversight:** The user is always shown the agent's extracted plan, parameter breakdown, and editable draft before any real-world action occurs.
3. **Deterministic Visual State Feedback:** Clear color-coded badges, step indicators, and execution timelines reflecting real-time status.

---

## 2. Visual Layout & Screen Wireframes

```text
+-----------------------------------------------------------------------------------------------+
|  AI TASK AUTOMATION ASSISTANT                  [ Status: OAuth Connected ] [ Mode: Enterprise]|
+-------------------------------+---------------------------------------------------------------+
|  SIDEBAR                      |  MAIN WORKSPACE                                               |
|                               |                                                               |
|  [ + New Task ]               |  +---------------------------------------------------------+  |
|                               |  | Natural Language Command Console                        |  |
|  * Integrations:              |  | [ Enter your enterprise instruction here...           ] |  |
|    - [x] Gmail (Active)       |  | [ Example Chips: Send Status Update | Request Review ]  |  |
|    - [ ] Docs (Coming soon)   |  | [ Execute Task Button ]                                 |  |
|                               |  +---------------------------------------------------------+  |
|  * Recent Task History:       |                                                               |
|    - #102: Status Email [OK]  |  +---------------------------------------------------------+  |
|    - #101: Review Req [OK]    |  | Plan & Draft Review Gate (HITL)                         |  |
|    - #100: Missing Info [ERR] |  | * Intent: Send project phase completion update          |  |
|                               |  | * Target Tool: gmail_send_tool (Consequential)         |  |
|  * Model Settings:            |  |                                                         |  |
|    - Provider: Gemini 1.5     |  | Recipient Email: [ dr.sharma@university.edu           ] |  |
|    - Temp: 0.2                |  | Subject:         [ Project Phase 1 Completion Review  ] |  |
|                               |  | Body Preview (Editable):                                |  |
|  * Quick Logs:                |  | +-----------------------------------------------------+ |  |
|    [ View Execution Trace ]   |  | | Dear Dr. Sharma,                                    | |  |
|                               |  | | Our team has completed Phase 1...                   | |  |
|                               |  | +-----------------------------------------------------+ |  |
|                               |  |                                                         |  |
|                               |  | [ Approve & Send Now ]    [ Modify Plan ]   [ Cancel ]  |  |
|                               |  +---------------------------------------------------------+  |
|                               |                                                               |
|                               |  +---------------------------------------------------------+  |
|                               |  | Real-Time Execution Timeline                            |  |
|                               |  | [✓] Ingested -> [✓] Planned -> [✓] Approved -> [✓] Sent |  |
|                               |  | Status: COMPLETED | Gmail Msg ID: 18f9e120bc7129ac      |  |
|                               |  +---------------------------------------------------------+  |
+-------------------------------+---------------------------------------------------------------+
```

---

## 3. Component Architecture & UI Elements

### 3.1 Streamlit Component Hierarchy
- `app.py`: Main application bootstrap, state initialization, and global page config.
- `components/sidebar.py`: Manages OAuth authentication status, active tools list, history list, and configuration toggles.
- `components/command_input.py`: Renders the primary text input area with quick-prompt chips.
- `components/clarification_modal.py`: Displays dynamic input fields when the agent requests missing information (e.g., recipient email).
- `components/draft_card.py`: Renders an interactive, editable form displaying recipient, subject, and body text with action buttons (**Approve & Send**, **Regenerate**, **Cancel**).
- `components/timeline.py`: Displays the step-by-step progress tracker.
- `components/log_drawer.py`: Collapsible expander displaying real-time structured execution logs and JSON payloads.

### 3.2 Status Badge Styling Specification

| State | Badge Color | Icon | Description |
|---|---|---|---|
| `IDLE` | Gray (`#6c757d`) | ⚪ | Ready for user instruction |
| `PARSING` | Blue (`#0d6efd`) | ⏳ | LLM analyzing intent and building plan |
| `CLARIFICATION`| Amber (`#ffc107`) | ❓ | Waiting for missing user parameters |
| `AWAITING_APPROVAL`| Purple (`#6f42c1`) | 👁️ | Draft ready for human review and sign-off |
| `EXECUTING` | Yellow (`#fd7e14`) | ⚡ | Tool executing external API dispatch |
| `COMPLETED` | Green (`#198754`) | ✅ | Successfully executed and verified |
| `FAILED` | Red (`#dc3545`) | ❌ | Execution error encountered |
| `CANCELLED` | Dark Gray (`#495057`)| 🚫 | User aborted task |

---

## 4. Streamlit Session State Management

Streamlit executes the full script on user interaction. To maintain state across runs, the following keys are preserved in `st.session_state`:

```python
# Session State Initialization Schema
DEFAULT_SESSION_STATE = {
    "session_id": "uuid-v4",
    "current_task": None,               # TaskPlan object
    "execution_state": "IDLE",          # WorkflowState enum
    "chat_history": [],                 # List of user & agent messages
    "clarification_needed": None,       # ClarificationRequest object
    "last_result": None,                # ToolResult object
    "authenticated_user_email": None,   # Current Gmail user
    "oauth_connected": False,           # Auth status boolean
    "execution_logs": []                # List of live log strings
}
```

---

## 5. User Interaction Flows (UX Walkthrough)

### 5.1 Standard Flow (Happy Path)
1. **User Input:** User enters *"Send project update email to advisor@edu.com"* and clicks **Execute**.
2. **Reasoning State:** Status indicator turns to `PARSING`. LLM extracts parameters and drafts the message.
3. **Approval State:** Status changes to `AWAITING_APPROVAL`. The UI expands the Draft Card showing recipient, subject, and formatted email body.
4. **User Action:** User reviews the draft, adjusts a sentence directly in the textarea, and clicks **Approve & Send**.
5. **Execution State:** Tool communicates with Gmail API. Status turns to `EXECUTING`.
6. **Completion State:** Upon 200 OK from Gmail, status turns to `COMPLETED`. A green success banner displays the Gmail Message ID with a timestamp.

### 5.2 Missing Information Flow (Clarification)
1. **User Input:** User enters *"Send an email to my project partner asking for the code repo link."*
2. **Ambiguity Detected:** Agent detects partner's email address is missing.
3. **Clarification UI:** UI renders: *"Please specify the email address of your project partner:"* with a text input.
4. **User Response:** User provides `partner@gmail.com` and clicks **Continue**.
5. **Resume Flow:** Agent synthesizes the plan and proceeds to the Draft Review Gate.
