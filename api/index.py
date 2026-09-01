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
# 7. Web Dashboard UI Route
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
        <title>AIRA - Autonomous AI Agent Dashboard</title>
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
            .main-grid {{ display: grid; grid-template-columns: 3fr 4fr 3fr; gap: 1.5rem; }}
            .card {{ background: var(--card); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
            .card-title {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; }}
            .chat-bubble {{ background: var(--primary-bg); padding: 1.2rem; border-radius: 12px; border-left: 4px solid var(--primary); margin-bottom: 1rem; }}
            .input-group {{ display: flex; gap: 0.5rem; margin-top: 1rem; }}
            .input-box {{ flex: 1; padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid #cbd5e1; outline: none; font-size: 0.9rem; }}
            .btn-send {{ background: var(--primary); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 10px; font-weight: 600; cursor: pointer; }}
            .activity-row {{ display: flex; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }}
            .badge {{ background: #ecfdf5; color: #10b981; padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.72rem; font-weight: 700; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1 class="title">🤖 AIRA - Autonomous AI Agent</h1>
                <div class="subtitle">Vercel Serverless Deployment • Intent Reasoning & Enterprise Automation</div>
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
            <div class="card">
                <div class="card-title">Recent Activity</div>
                <div class="activity-row"><span>✉️ Email sent to Chetan</span><strong>10:30 AM</strong></div>
                <div class="activity-row"><span>📄 Document summary created</span><strong>09:15 AM</strong></div>
                <div class="activity-row"><span>📅 Meeting scheduled</span><strong>09:00 AM</strong></div>
                <div class="activity-row"><span>📊 Data extracted sales.xlsx</span><strong>Yesterday</strong></div>
            </div>

            <div class="card">
                <div class="card-title">🤖 AI Assistant Command Console</div>
                <div class="chat-bubble">
                    <strong>Hi Vaishnavi! 👋</strong><br>
                    AIRA serverless agent is ready to automate your tasks.
                </div>
                <div class="input-group">
                    <input id="promptInput" class="input-box" placeholder="Ask anything (e.g., 'Send email to Chetan about project update')...">
                    <button onclick="sendCommand()" class="btn-send">Send 🚀</button>
                </div>
                <div id="outputLog" style="margin-top: 1rem; font-size: 0.84rem; font-family: monospace; color: #1e293b; background: #f1f5f9; padding: 0.8rem; border-radius: 8px; display: none;"></div>
            </div>

            <div class="card">
                <div class="card-title">Today's Schedule</div>
                <div class="activity-row"><span>09:00 AM • Daily Standup</span><span class="badge">30m</span></div>
                <div class="activity-row"><span>11:00 AM • Team Sync</span><span class="badge">1h</span></div>
                <div class="activity-row"><span>02:00 PM • Client Presentation</span><span class="badge">1h</span></div>
                <div class="activity-row"><span>04:30 PM • Review & Planning</span><span class="badge">30m</span></div>
            </div>
        </div>

        <script>
            async function sendCommand() {{
                const input = document.getElementById('promptInput').value.trim();
                const log = document.getElementById('outputLog');
                if (!input) return;
                log.style.display = 'block';
                log.innerText = '⏳ AIRA analyzing intent and synthesizing task plan...';
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
