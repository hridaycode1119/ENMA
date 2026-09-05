"""
AIRA Enterprise AI Agent - Vercel Serverless Application Entrypoint.
FastAPI ASGI application exposing REST endpoints and web UI for Vercel deployment.
"""

import os
import sys
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.orchestrator import AgentOrchestrator, WorkflowState
from agent.parser import IntentParser
from tools.registry import ToolRegistry
from database.repository import AIRARepository
from database.supabase_client import SupabaseManager
from modules.documents.parsers import DocumentParserFactory
from modules.documents.editor import DocumentEditor

# Initialize FastAPI App (Top-Level ASGI variable for Vercel)
app = FastAPI(
    title="AIRA Autonomous AI Agent API",
    description="Serverless REST API and Cognitive Engine for Enterprise Task Automation",
    version="2.4.0",
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singletons
orchestrator = AgentOrchestrator()
repo = AIRARepository()
doc_editor = DocumentEditor()

# Request Schemas
class CommandRequest(BaseModel):
    instruction: str
    context: Optional[Dict[str, Any]] = None

class ClarificationRequest(BaseModel):
    responses: Dict[str, Any]

class ExecuteRequest(BaseModel):
    override_parameters: Optional[Dict[str, Any]] = None

class CalendarRequest(BaseModel):
    title: str
    event_time: str
    duration: Optional[str] = "30 mins"
    attendees: Optional[List[str]] = None

class DocEditRequest(BaseModel):
    text: str
    instruction: str
    tone: Optional[str] = "professional"

class NoteRequest(BaseModel):
    title: str
    content: str
    category: Optional[str] = "note"

class ResendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    from_email: Optional[str] = None
    reply_to: Optional[str] = None

# ------------------------------------------------------------------------------
# 1. Health & Status
# ------------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    sb_mgr = SupabaseManager()
    is_sb, sb_msg = sb_mgr.ping()
    return {
        "status": "healthy",
        "service": "AIRA Autonomous AI Agent",
        "version": "2.4.0",
        "engine": "Gemini 1.5 Flash + Tool Registry",
        "supabase_connected": is_sb,
        "supabase_diagnostic": sb_msg,
        "tools_count": len(ToolRegistry().list_tool_names()),
    }

# ------------------------------------------------------------------------------
# 2. Agent Cognitive Reasoning Endpoints
# ------------------------------------------------------------------------------
@app.post("/api/agent/command")
def submit_command(req: CommandRequest):
    if not req.instruction.strip():
        raise HTTPException(status_code=400, detail="Instruction cannot be empty.")
    try:
        plan = orchestrator.submit_instruction(req.instruction, context=req.context)
        return {
            "task_id": plan.task_id,
            "task_type": plan.task_type.value,
            "intent_summary": plan.intent_summary,
            "state": orchestrator.state.value,
            "target_tool": plan.target_tool,
            "tool_parameters": plan.tool_parameters,
            "requires_clarification": plan.requires_clarification,
            "clarification": plan.clarification.to_dict() if plan.clarification else None,
            "latency_ms": orchestrator.last_execution_time_ms,
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@app.post("/api/agent/clarification")
def submit_clarification(req: ClarificationRequest):
    try:
        plan = orchestrator.submit_clarification(req.responses)
        return {
            "task_id": plan.task_id,
            "state": orchestrator.state.value,
            "tool_parameters": plan.tool_parameters,
            "requires_clarification": plan.requires_clarification,
        }
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@app.post("/api/agent/execute")
def execute_task(req: ExecuteRequest):
    try:
        result = orchestrator.execute_confirmed_task(override_parameters=req.override_parameters)
        return {
            "success": result.success,
            "state": orchestrator.state.value,
            "data": result.data,
            "external_reference_id": result.external_reference_id,
            "error_message": result.error_message,
            "execution_time_ms": result.execution_time_ms,
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# ------------------------------------------------------------------------------
# 3. Tasks & Metrics
# ------------------------------------------------------------------------------
@app.get("/api/tasks")
def get_tasks(limit: int = 10):
    return {
        "metrics": repo.get_task_metrics(),
        "recent_tasks": repo.get_recent_tasks(limit=limit),
    }

# ------------------------------------------------------------------------------
# 4. Calendar & Scheduling
# ------------------------------------------------------------------------------
@app.get("/api/calendar")
def get_calendar():
    return {"events": repo.get_calendar_events()}

@app.post("/api/calendar/schedule")
def schedule_event(req: CalendarRequest):
    from tools.calendar.calendar_tool import CalendarScheduleTool
    cal_tool = CalendarScheduleTool()
    res = cal_tool.execute({
        "title": req.title,
        "time": req.event_time,
        "duration": req.duration,
        "attendees": req.attendees or [],
    })
    return res.data

# ------------------------------------------------------------------------------
# 5. Document AI Editing
# ------------------------------------------------------------------------------
@app.post("/api/documents/edit")
def edit_document(req: DocEditRequest):
    try:
        new_text, summary = doc_editor.execute_ai_command(
            document_text=req.text,
            instruction=req.instruction,
            tone=req.tone,
        )
        return {
            "edited_text": new_text,
            "summary": summary,
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# ------------------------------------------------------------------------------
# 6. Notes & Journals
# ------------------------------------------------------------------------------
@app.get("/api/notes")
def get_notes(category: str = "note"):
    return {"notes": repo.get_notes(category=category)}

@app.post("/api/notes")
def create_note(req: NoteRequest):
    saved = repo.save_note(
        title=req.title,
        content=req.content,
        category=req.category or "note",
    )
    return saved

# ------------------------------------------------------------------------------
# 7. Resend Email Delivery
# ------------------------------------------------------------------------------
@app.post("/api/resend/send")
def send_resend_email(req: ResendEmailRequest):
    from integrations.resend_client import ResendClient
    client = ResendClient()
    try:
        res = client.send_email(
            to=req.to,
            subject=req.subject,
            text=req.body,
            from_email=req.from_email,
            reply_to=req.reply_to,
        )
        return res
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# ------------------------------------------------------------------------------
# 8. Prebuilt Email Templates & Custom Composer
# ------------------------------------------------------------------------------
@app.get("/api/templates")
def get_email_templates():
    from components.email_composer import PREBUILT_TEMPLATES
    return {"templates": PREBUILT_TEMPLATES}

# ------------------------------------------------------------------------------
# 9. Web Dashboard UI Route
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index_page():
    metrics = repo.get_task_metrics()
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIRA - Autonomous AI Agent & Email Studio</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --muted: #64748b;
                --primary: #6d28d9; --primary-light: #7c3aed; --primary-bg: #f5f3ff;
                --success: #10b981; --warning: #f59e0b; --border: #f1f5f9;
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); padding: 2rem 3rem; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }}
            .title {{ font-size: 1.8rem; font-weight: 800; }}
            .subtitle {{ color: var(--muted); font-size: 0.95rem; margin-top: 0.3rem; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 2rem; }}
            .kpi-card {{ background: var(--card); padding: 1.2rem; border-radius: 14px; border: 1px solid var(--border); box-shadow: 0 4px 15px rgba(0,0,0,0.03); }}
            .kpi-val {{ font-size: 1.6rem; font-weight: 800; }}
            .kpi-label {{ color: var(--muted); font-size: 0.82rem; font-weight: 600; text-transform: uppercase; margin-top: 0.2rem; }}
            .main-grid {{ display: grid; grid-template-columns: 3.5fr 5fr 3.5fr; gap: 1.5rem; }}
            .card {{ background: var(--card); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
            .card-title {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; }}
            .input-box {{ width: 100%; padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid #cbd5e1; outline: none; font-size: 0.9rem; margin-bottom: 0.8rem; }}
            .textarea-box {{ width: 100%; padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid #cbd5e1; outline: none; font-size: 0.9rem; margin-bottom: 0.8rem; min-height: 120px; font-family: inherit; }}
            .btn-send {{ background: var(--primary); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 10px; font-weight: 600; cursor: pointer; width: 100%; }}
            .btn-tmpl {{ background: var(--primary-bg); color: var(--primary); border: 1px solid #ddd6fe; padding: 0.4rem 0.8rem; border-radius: 8px; font-size: 0.78rem; font-weight: 600; cursor: pointer; margin-right: 0.4rem; margin-bottom: 0.4rem; }}
            .btn-tmpl:hover {{ background: #ede9fe; }}
            .activity-row {{ display: flex; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }}
            .badge {{ background: #ecfdf5; color: #10b981; padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.72rem; font-weight: 700; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1 class="title">🤖 AIRA - AI Agent & Email Studio</h1>
                <div class="subtitle">Vercel Serverless Deployment • Resend API • Custom Composer & Prebuilt Templates</div>
            </div>
            <span class="badge" style="font-size: 0.85rem; padding: 0.4rem 0.9rem;">🟢 Vercel Serverless Active</span>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-val" style="color: #6d28d9;">{metrics['completed']}</div><div class="kpi-label">Tasks Completed</div></div>
            <div class="kpi-card"><div class="kpi-val" style="color: #10b981;">{metrics['emails_sent']}</div><div class="kpi-label">Emails Sent</div></div>
            <div class="kpi-card"><div class="kpi-val" style="color: #f59e0b;">{metrics['events_today']}</div><div class="kpi-label">Events Today</div></div>
            <div class="kpi-card"><div class="kpi-val" style="color: #3b82f6;">{metrics['files_processed']}</div><div class="kpi-label">Files Processed</div></div>
            <div class="kpi-card"><div class="kpi-val" style="color: #8b5cf6;">{metrics['time_saved_hours']}h</div><div class="kpi-label">Time Saved</div></div>
        </div>

        <div class="main-grid">
            <!-- Left: Natural Language AI Assistant -->
            <div class="card">
                <div class="card-title">🤖 AI Prompt Console</div>
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.8rem;">Enter instruction to analyze with Gemini reasoning:</p>
                <textarea id="promptInput" class="textarea-box" style="min-height: 80px;" placeholder="e.g., Send email to hriday.code1119@gmail.com with subject Project Status..."></textarea>
                <button onclick="sendCommand()" class="btn-send" style="background: #475569;">Analyze Intent ⚡</button>
                <div id="outputLog" style="margin-top: 1rem; font-size: 0.8rem; font-family: monospace; color: #1e293b; background: #f1f5f9; padding: 0.8rem; border-radius: 8px; display: none;"></div>
            </div>

            <!-- Middle: Custom Email Composer & Prebuilt Templates -->
            <div class="card">
                <div class="card-title">✉️ Custom Email Composer</div>
                <div style="margin-bottom: 0.8rem;">
                    <div style="font-size: 0.8rem; font-weight: 600; color: #64748b; margin-bottom: 0.4rem;">PREBUILT TEMPLATES:</div>
                    <button class="btn-tmpl" onclick="loadTemplate('status')">📊 Project Status</button>
                    <button class="btn-tmpl" onclick="loadTemplate('meeting')">📅 Meeting Request</button>
                    <button class="btn-tmpl" onclick="loadTemplate('academic')">🎓 BTech Progress</button>
                    <button class="btn-tmpl" onclick="loadTemplate('urgent')">🚨 Urgent Alert</button>
                </div>
                
                <input id="emailTo" class="input-box" placeholder="Recipient email(s) (e.g. hriday.code1119@gmail.com)" />
                <input id="emailSubject" class="input-box" placeholder="Subject line" />
                <textarea id="emailBody" class="textarea-box" placeholder="Write custom mail message body here..."></textarea>
                
                <button onclick="sendCustomEmail()" class="btn-send">🚀 Send Live via Resend</button>
                <div id="emailStatus" style="margin-top: 0.8rem; font-size: 0.84rem; font-weight: 600; display: none;"></div>
            </div>

            <!-- Right: Activity & Schedule -->
            <div class="card">
                <div class="card-title">Recent Activity</div>
                <div class="activity-row"><span>✉️ Email sent to Hriday</span><strong>Just now</strong></div>
                <div class="activity-row"><span>📄 Document summary created</span><strong>09:15 AM</strong></div>
                <div class="activity-row"><span>📅 Meeting scheduled</span><strong>09:00 AM</strong></div>
                <div class="activity-row"><span>📊 Data extracted sales.xlsx</span><strong>Yesterday</strong></div>
                
                <div class="card-title" style="margin-top: 1.5rem;">Today's Schedule</div>
                <div class="activity-row"><span>09:00 AM • Daily Standup</span><span class="badge">30m</span></div>
                <div class="activity-row"><span>02:00 PM • Client Demo</span><span class="badge">1h</span></div>
            </div>
        </div>

        <script>
            const templates = {{
                status: {{
                    subject: "[Update] Project Status Report: Milestones Completed",
                    body: "Hi Team,\\n\\nHere is our project progress report:\\n• Completed: AI Core, Multi-Format Document Studio, and Supabase integration.\\n• Tests: 100% automated test coverage.\\n• Next: Live user validation.\\n\\nBest regards,\\nAIRA Team"
                }},
                meeting: {{
                    subject: "Meeting Request: Sprint Planning & Architecture Sync",
                    body: "Dear Team,\\n\\nI would like to schedule a sync meeting to review upcoming deliverables.\\n\\nProposed Agenda:\\n1. Review Phase 5 & 6 features.\\n2. Live demo of Resend email automation.\\n\\nBest regards,\\nAIRA Team"
                }},
                academic: {{
                    subject: "BTech Major Project: Bi-Weekly Progress Submission",
                    body: "Respected Advisor,\\n\\nPlease find attached our progress report for the Autonomous AI Agent project.\\nTeam: Vaishnavi Dhyani, Chetan, Hriday.\\nAll benchmarks achieved 100% accuracy.\\n\\nSincerely,\\nProject Team"
                }},
                urgent: {{
                    subject: "URGENT: Action Required on Production Task Pipeline",
                    body: "Hello,\\n\\nThis is an automated priority alert regarding system task execution.\\nPlease review the logs immediately.\\n\\nThank you,\\nAIRA Monitoring System"
                }}
            }};

            function loadTemplate(key) {{
                const t = templates[key];
                if (!t) return;
                document.getElementById('emailSubject').value = t.subject;
                document.getElementById('emailBody').value = t.body;
            }}

            async function sendCustomEmail() {{
                const to = document.getElementById('emailTo').value.trim();
                const subject = document.getElementById('emailSubject').value.trim();
                const body = document.getElementById('emailBody').value.trim();
                const status = document.getElementById('emailStatus');
                if (!to || !subject || !body) {{
                    alert('Please fill in Recipient, Subject, and Body fields.');
                    return;
                }}
                status.style.display = 'block';
                status.style.color = '#6d28d9';
                status.innerText = '⏳ Dispatching email via Resend API...';
                try {{
                    const res = await fetch('/api/resend/send', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ to, subject, body }})
                    }});
                    const data = await res.json();
                    if (res.ok) {{
                        status.style.color = '#10b981';
                        status.innerText = '🎉 Email dispatched successfully! ID: ' + (data.id || 'sent');
                    }} else {{
                        status.style.color = '#ef4444';
                        status.innerText = '❌ Error: ' + (data.detail || JSON.stringify(data));
                    }}
                }} catch (err) {{
                    status.style.color = '#ef4444';
                    status.innerText = '❌ Network Error: ' + err.message;
                }}
            }}

            async function sendCommand() {{
                const input = document.getElementById('promptInput').value.trim();
                const log = document.getElementById('outputLog');
                if (!input) return;
                log.style.display = 'block';
                log.innerText = '⏳ AIRA analyzing intent...';
                try {{
                    const res = await fetch('/api/agent/command', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ instruction: input }})
                    }});
                    const data = await res.json();
                    log.innerText = '✅ Task Plan Synthesized:\\n' + JSON.stringify(data, null, 2);
                }} catch (err) {{
                    log.innerText = '❌ Error: ' + err.message;
                }}
            }}
        </script>
    </body>
    </html>
    """

