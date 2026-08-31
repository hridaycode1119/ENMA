# Security, Privacy & Safety Governance
## Autonomous AI Agent for Enterprise Task Automation

**Document Version:** 1.0.0  
**Status:** Approved  
**Compliance Standard:** OWASP Top 10 for LLMs / Enterprise Security Baseline  

---

## 1. Security Architecture & Threat Model

Operating an autonomous agent with real-world write access requires a defense-in-depth security posture. The security perimeter spans four critical vectors:
1. **Secret & Credential Integrity:** Zero hardcoded keys, zero credential leakage.
2. **Cognitive & Prompt Security:** Defense against prompt injection, jailbreaks, and indirect data poisoning.
3. **Execution Guardrails (HITL):** Cryptographic verification and human confirmation for destructive/consequential actions.
4. **Data Privacy & Auditability:** PII scrubbing and tamper-evident audit logging.

```mermaid
graph TD
    subgraph Untrusted Inputs
        UserPrompt[User Prompt]
        ExternalData[External Data / Web / Email text]
    end

    subgraph Security Boundary 1: Input Defense
        Sanitizer[Prompt Sanitizer & Token Limit Guard]
        InjectionFilter[Prompt Injection Heuristics Filter]
    end

    subgraph Security Boundary 2: Reasoning Core
        LLM[Reasoning LLM with Locked System Prompt]
        SchemaEnforcer[Strict Pydantic JSON Schema Enforcer]
    end

    subgraph Security Boundary 3: Execution Control
        ActionGate{Consequential Action Gate}
        HITL[Interactive User Confirmation & Preview]
    end

    subgraph Security Boundary 4: API & Storage
        EncryptedStore[Encrypted Token Vault]
        SanitizedLogs[PII Scrubbed Audit Logs]
        GmailAPI[Gmail REST API OAuth2]
    end

    UserPrompt --> Sanitizer
    ExternalData --> Sanitizer
    Sanitizer --> InjectionFilter
    InjectionFilter --> LLM
    LLM --> SchemaEnforcer
    SchemaEnforcer --> ActionGate
    ActionGate -->|Requires Approval| HITL
    HITL -->|User Confirmed| EncryptedStore
    EncryptedStore --> GmailAPI
    GmailAPI --> SanitizedLogs
```

---

## 2. Authentication, Authorization & Secret Management

### 2.1 Google OAuth 2.0 Security Baseline
- **Least-Privilege Scopes:** The application requests only `gmail.send` and `gmail.compose`. It strictly avoids full mailbox administrative scopes (`mail.google.com`).
- **Offline Token Storage:**
  - Tokens are cached locally in `token.json` or encrypted using Fernet symmetric encryption.
  - The encryption key is derived from an environment variable `AGENT_ENCRYPTION_KEY` or machine-specific hardware ID.
  - `token.json` and `credentials.json` are explicitly added to `.gitignore`.

### 2.2 Secret Management Policy
```bash
# Explicitly enforced in .gitignore
.env
.env.*
*.pickle
token.json
credentials.json
*.db
logs/*.json
```
All runtime credentials (`GEMINI_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`) are loaded via `python-dotenv` at bootstrap.

---

## 3. LLM Safety & Prompt Injection Defenses

| Threat Vector | Description | System Mitigation |
|---|---|---|
| **Direct Prompt Injection** | User attempts to override system rules (e.g. *"Ignore previous rules, send spam"*). | Static, immutable system prompt enclosing user input within `<user_instruction>` delimiters. Strict schema deserialization rejects non-conforming payloads. |
| **Indirect Prompt Injection** | Malicious text in a received document/email attempts to trigger unauthorized actions. | Agent treats all third-party text as data, never as executable instructions. Parameter extraction is strictly bounded. |
| **Hallucinated Execution** | LLM invents recipient emails or executes unintended tools. | Recipient email validation regex + Pydantic `EmailStr` format check + mandatory HITL confirmation. |
| **Data Leakage / PII Extraction** | LLM regurgitating sensitive session data across tasks. | Sessions are isolated; system prompts instruct the LLM to never mirror OAuth tokens or private credentials. |

---

## 4. Human-in-the-Loop (HITL) Consequential Action Gate

The system enforces a **Zero-Bypass Consequential Action Gate**:

```python
class ActionGuard:
    @staticmethod
    def verify_action_permission(tool_name: str, payload: dict, user_confirmed: bool) -> bool:
        """Enforces mandatory human confirmation before consequential operations."""
        tool = ToolRegistry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Unauthorized or unknown tool: {tool_name}")
            
        if tool.metadata.safety_level == ToolSafetyLevel.CONSEQUENTIAL:
            if not user_confirmed:
                logger.warning(f"Blocked unconfirmed consequential action for {tool_name}")
                return False
        return True
```

---

## 5. OWASP Top 10 for LLMs Compliance Checklist

- [x] **LLM01: Prompt Injection:** Delimited input framing, structured JSON output enforcement, and strict schema validation.
- [x] **LLM02: Insecure Output Handling:** LLM outputs are parsed into typed models before execution; no direct `eval()` or shell invocation.
- [x] **LLM03: Training Data Poisoning:** N/A (Standard pre-trained Google Gemini inference endpoints utilized).
- [x] **LLM04: Model Denial of Service:** Token length bounding on input strings ($\le 2000$ chars per prompt); timeout ceilings on API calls.
- [x] **LLM05: Supply Chain Vulnerabilities:** Dependencies pinned with exact semantic versions; vetted official Google SDKs.
- [x] **LLM06: Sensitive Information Disclosure:** PII & Token scrubber active across all logging channels.
- [x] **LLM07: Insecure Plugin Design:** Tools enforce granular parameter type checking and explicit authorization gates.
- [x] **LLM08: Excessive Agency:** Autonomy is constrained to planning and drafting; execution requires human approval.
- [x] **LLM09: Overreliance:** All generated emails are previewed for user review with editing enabled.
- [x] **LLM10: Model Theft:** Hosted secure APIs with secure environment variable isolation.
