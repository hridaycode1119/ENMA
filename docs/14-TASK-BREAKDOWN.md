# Work Breakdown Structure & Task Allocation Specification
## Autonomous AI Agent for Enterprise Task Automation

**Document Version:** 1.0.0  
**Status:** Approved  
**Team Members:** Vaishnavi Dhyani, Chetan, Hriday  

---

## 1. Responsibility Assignment Matrix (RACI)

| Work Package | Vaishnavi Dhyani | Chetan | Hriday |
|---|---|---|---|
| **AI & Prompt Engineering** | **Accountable (A)** | Informed (I) | Consulted (C) |
| **Backend & Tool Registry** | Consulted (C) | **Accountable (A)** | Informed (I) |
| **Frontend & UI / UX** | Consulted (C) | Informed (I) | **Accountable (A)** |
| **Database & Persistence** | Informed (I) | **Accountable (A)** | Consulted (C) |
| **Testing & Evaluation** | Responsible (R) | Responsible (R) | **Accountable (A)** |
| **Documentation & Demo** | Responsible (R) | Responsible (R) | **Accountable (A)** |

---

## 2. Granular Task Breakdown (WBS)

### 2.1 Track A: AI Engine & Reasoning (Vaishnavi Dhyani)

| Task ID | Task Description | Est. Hours | Prerequisite | Deliverable File(s) | Status |
|---|---|---|---|---|---|
| **TSK-AI-01** | Define Pydantic models for intent, plan, draft, and clarification | 6h | PRD Approved | `schemas/task_schemas.py` | ✅ Completed |
| **TSK-AI-02** | Engineer system prompts and few-shot examples for email workflows | 8h | TSK-AI-01 | `agent/prompts.py` | ✅ Completed |
| **TSK-AI-03** | Implement Gemini API LLM adapter with structured JSON enforcement | 10h | TSK-AI-02 | `agent/llm_adapter.py` | ✅ Completed |
| **TSK-AI-04** | Develop intent parser & ambiguity detection logic | 10h | TSK-AI-03 | `agent/parser.py` | ✅ Completed |
| **TSK-AI-05** | Build LLM evaluation benchmark suite & test edge cases | 12h | TSK-AI-04 | `tests/evals/test_reasoning.py` | ✅ Completed |

### 2.2 Track B: Backend, APIs & Data Layer (Chetan)

| Task ID | Task Description | Est. Hours | Prerequisite | Deliverable File(s) | Status |
|---|---|---|---|---|---|
| **TSK-BE-01** | Implement Google OAuth 2.0 flow & token refresh manager | 10h | GCP Setup | `integrations/oauth_handler.py` | ✅ Completed |
| **TSK-BE-02** | Build RFC 2822 MIME builder and Gmail REST API Client | 12h | TSK-BE-01 | `integrations/gmail_client.py` | ✅ Completed |
| **TSK-BE-03** | Implement `BaseTool` abstraction and dynamic `ToolRegistry` | 8h | TSK-AI-01 | `tools/base.py`, `tools/registry.py` | ✅ Completed |
| **TSK-BE-04** | Build `GmailSendTool` and `GmailDraftTool` adapters | 8h | TSK-BE-02, TSK-BE-03 | `tools/gmail/gmail_tool.py` | ✅ Completed |
| **TSK-BE-05** | Implement SQLite database models & SQLAlchemy ORM layer | 10h | Architecture Spec | `db/database.py`, `db/models.py` | 📋 Pending |
| **TSK-BE-06** | Implement Loguru structured logger with PII / Token scrubber | 6h | TSK-BE-05 | `logging/logger.py`, `security/sanitizer.py` | 📋 Pending |

### 2.3 Track C: Frontend & System Integration (Hriday)

| Task ID | Task Description | Est. Hours | Prerequisite | Deliverable File(s) | Status |
|---|---|---|---|---|---|
| **TSK-FE-01** | Bootstrap Streamlit application & setup modern layout structure | 6h | Architecture Spec | `app.py`, `assets/style.css` | ✅ Completed |
| **TSK-FE-02** | Develop conversational task input console & quick prompt chips | 8h | TSK-FE-01 | `components/command_input.py` | ✅ Completed |
| **TSK-FE-03** | Build interactive Human-in-the-Loop (HITL) Draft Review Card | 12h | TSK-AI-01, TSK-FE-01 | `components/draft_card.py` | ✅ Completed |
| **TSK-FE-04** | Implement real-time status timeline and badge indicators | 8h | TSK-FE-01 | `components/timeline.py` | ✅ Completed |
| **TSK-FE-05** | Develop sidebar with OAuth connection status & task history view | 10h | TSK-BE-05, TSK-FE-01 | `components/sidebar.py`, `components/history.py` | ✅ Completed |
| **TSK-FE-06** | Wire end-to-end frontend with agent controller and tool registry | 14h | Tracks A, B, C | `agent/orchestrator.py`, `app.py` | ✅ Completed |
| **TSK-FE-07** | Build automated PyTest integration and Streamlit AppTest suites | 12h | TSK-FE-06 | `tests/e2e/test_app_flow.py` | ✅ Completed |

---

## 3. Sprint Schedule

- **Sprint 1 (Weeks 1-2):** Foundational Schemas, GCP Setup, OAuth Flow, Base Streamlit Skeleton.
- **Sprint 2 (Weeks 3-4):** LLM Reasoning Engine, Prompt Engineering, Gmail REST API Client, Tool Registry.
- **Sprint 3 (Weeks 5-6):** Interactive HITL UI, Full Agent Orchestration, SQLite DB Persistence.
- **Sprint 4 (Weeks 7-8):** Edge Case Handling, Automated Test Suite, End-to-End Hardening & Demo Preparation.
