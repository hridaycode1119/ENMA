"""
ENMA Enterprise AI Agent - Vercel Serverless Application Entrypoint.
Tagline: Intelligence That Gets Work Done
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
from database.repository import ENMARepository, LUCORARepository, AIRARepository
from database.supabase_client import SupabaseManager
from modules.documents.parsers import DocumentParserFactory
from modules.documents.editor import DocumentEditor

# Initialize FastAPI App (Top-Level ASGI variable for Vercel)
app = FastAPI(
    title="ENMA Autonomous AI Agent API",
    description="Serverless REST API and Cognitive Engine for Enterprise Task Automation — Intelligence That Gets Work Done",
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
repo = ENMARepository()
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
        "service": "ENMA Autonomous AI Agent",
        "tagline": "Intelligence That Gets Work Done",
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
    return """<!DOCTYPE html><html class="dark" lang="en" style=""><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>ENMA by LUCORA - Enterprise AI Workspace</title>
<!-- Tailwind CSS v3 with plugins -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<!-- Tailwind Configuration for Custom Wine/Plum Palette -->
<script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            wine: {
              950: '#14060d',
              900: '#1a0b12',
              850: '#230c18',
              800: '#2b101f',
              750: '#341426',
              700: '#3f172e',
              600: '#521f3d',
              500: '#752b57',
            },
            ruby: {
              400: '#fb719e',
              500: '#f43f76',
              600: '#e11d5e',
              700: '#be124c',
            },
            accent: {
              pink: '#ff4d8d',
              glow: '#e23c72',
              soft: '#fce7f3',
              muted: '#a88094',
            }
          },
          fontFamily: {
            sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            serif: ['Playfair Display', 'Georgia', 'serif'],
            handwriting: ['Caveat', 'Dancing Script', 'cursive'],
          }
        }
      }
    }
  </script>
<!-- Google Fonts: Inter & Caveat for cursive accent -->
<link href="https://fonts.googleapis.com" rel="preconnect">
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect">
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;600&amp;family=Inter:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet">
<!-- Custom Styles for Glowing Waves, Ambient Shadows and Glassmorphism -->
<style data-purpose="custom-decorations">
    /* Fluid glowing gradient waves */
    .hero-wave {
      background: radial-gradient(circle at 75% 45%, rgba(244, 63, 118, 0.45) 0%, rgba(225, 29, 94, 0.25) 35%, rgba(43, 16, 31, 0) 70%),
                  linear-gradient(135deg, transparent 40%, rgba(255, 77, 141, 0.2) 65%, rgba(226, 60, 114, 0.35) 85%);
      position: absolute;
      inset: 0;
      pointer-events: none;
      border-radius: 1rem;
    }

    .sidebar-wave {
      background: radial-gradient(ellipse at bottom right, rgba(226, 60, 114, 0.4) 0%, rgba(190, 18, 76, 0.25) 40%, transparent 75%);
      position: absolute;
      bottom: 60px;
      left: 0;
      right: 0;
      height: 140px;
      pointer-events: none;
      filter: blur(14px);
    }

    .footer-wave {
      background: radial-gradient(ellipse at 85% 100%, rgba(244, 63, 118, 0.45) 0%, rgba(190, 18, 76, 0.15) 50%, transparent 75%);
      position: absolute;
      bottom: 0;
      right: 0;
      width: 480px;
      height: 100px;
      pointer-events: none;
      filter: blur(12px);
    }

    /* Subtle custom scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #1a0b12;
    }
    ::-webkit-scrollbar-thumb {
      background: #3f172e;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #521f3d;
    }

    /* Soundwave bars animation */
    @keyframes wave-bounce {
      0%, 100% { height: 6px; }
      50% { height: 28px; }
    }
    .wave-bar {
      animation: wave-bounce 1.2s ease-in-out infinite;
    }
    .wave-bar:nth-child(2) { animation-delay: 0.1s; }
    .wave-bar:nth-child(3) { animation-delay: 0.2s; }
    .wave-bar:nth-child(4) { animation-delay: 0.3s; }
    .wave-bar:nth-child(5) { animation-delay: 0.4s; }
    .wave-bar:nth-child(6) { animation-delay: 0.5s; }
    .wave-bar:nth-child(7) { animation-delay: 0.6s; }
    .wave-bar:nth-child(8) { animation-delay: 0.5s; }
    .wave-bar:nth-child(9) { animation-delay: 0.35s; }
    .wave-bar:nth-child(10) { animation-delay: 0.15s; }
  </style>
</head>
<body class="bg-wine-900 text-[#fce7f3] font-sans antialiased overflow-x-hidden min-h-screen flex selection:bg-ruby-500 selection:text-white">
<!-- BEGIN: SidebarNavigation -->
<aside class="w-[248px] shrink-0 min-h-screen bg-wine-950/80 border-r border-wine-800 flex flex-col justify-between relative z-20" data-purpose="sidebar">
<!-- Top Branding & Navigation -->
<div class="p-4 flex flex-col gap-5">
<!-- App Brand Logo -->
<div class="flex items-center gap-2.5 px-2 pt-1">
<div class="w-7 h-7 flex items-center justify-center text-ruby-400">
<svg class="w-6 h-6 fill-current drop-shadow-[0_0_8px_rgba(244,63,118,0.7)]" viewBox="0 0 24 24">
<path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"></path>
</svg>
</div>
<div class="leading-tight">
<h1 class="text-sm font-bold tracking-wider text-white uppercase flex items-center gap-1">ENMA</h1>
<p class="text-[10px] tracking-widest text-accent-muted font-medium uppercase">by LUCORA</p>
</div>
</div>
<!-- Main Navigation Menu -->
<nav class="flex flex-col gap-1 text-[13px] font-medium" data-purpose="main-nav">
<!-- Active Pill Item: Home -->
<a class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-wine-800 text-white shadow-sm border border-ruby-500/20 font-semibold group transition" href="#">
<svg class="w-4 h-4 text-ruby-400 group-hover:scale-110 transition" fill="currentColor" viewBox="0 0 20 20">
<path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
</svg>
<span class="">Home</span>
</a>
<!-- Email Studio -->
<a class="flex items-center gap-3 px-3.5 py-2 rounded-xl text-accent-muted hover:text-white hover:bg-wine-850/60 transition" href="#">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<rect height="16" rx="2" width="20" x="2" y="4"></rect><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
</svg>
<span class="">Email Studio</span>
</a>
<!-- Calendar & Events -->
<a class="flex items-center gap-3 px-3.5 py-2 rounded-xl text-accent-muted hover:text-white hover:bg-wine-850/60 transition" href="#">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<rect height="18" rx="2" width="18" x="3" y="4"></rect><path d="M16 2v4M8 2v4M3 10h18"></path>
</svg>
<span class="">Calendar &amp; Events</span>
</a>
<!-- Document & Data Studio -->
<a class="flex items-center gap-3 px-3.5 py-2 rounded-xl text-accent-muted hover:text-white hover:bg-wine-850/60 transition" href="#">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"></path>
</svg>
<span class="">Document &amp; Data Studio</span>
</a>
<!-- Notes & Knowledge -->
<a class="flex items-center gap-3 px-3.5 py-2 rounded-xl text-accent-muted hover:text-white hover:bg-wine-850/60 transition" href="#">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"></path><path d="M6 6h10M6 10h10"></path>
</svg>
<span class="">Notes &amp; Knowledge</span>
</a>
<!-- Task & Email Studio -->
<a class="flex items-center gap-3 px-3.5 py-2 rounded-xl text-accent-muted hover:text-white hover:bg-wine-850/60 transition" href="#">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
</svg>
<span class="">Task &amp; Email Studio</span>
</a>
</nav>
<!-- System & Engine Section -->
<div class="pt-3 border-t border-wine-800/60 flex flex-col gap-1">
<h2 class="px-3.5 text-[10px] font-bold tracking-wider text-accent-muted/70 uppercase mb-1">SYSTEM &amp; ENGINE</h2>
<a class="flex items-center gap-3 px-3.5 py-2 rounded-xl text-accent-muted hover:text-white hover:bg-wine-850/60 transition text-[13px]" href="#">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"></path>
</svg>
<span class="">Voice Assistant</span>
</a>
<a class="flex items-center gap-3 px-3.5 py-2 rounded-xl text-accent-muted hover:text-white hover:bg-wine-850/60 transition text-[13px]" href="#">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
</svg>
<span class="">Command Center &amp; Settings</span>
</a>
</div>
</div>
<!-- Bottom Sidebar Section (Waves, Pro Card & User Profile) -->
<div class="p-3 relative flex flex-col gap-3">
<!-- Glow wave background illusion behind upgrade card -->
<div class="sidebar-wave"></div>
<!-- ENMA Pro Banner -->
<div class="relative z-10 bg-wine-850/90 border border-ruby-500/20 backdrop-blur-md rounded-2xl p-3.5 shadow-lg">
<div class="flex items-center gap-1.5 text-ruby-400 font-semibold text-xs mb-1">
<svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
<span class="tracking-wide">ENMA PRO</span>
</div>
<p class="text-[11px] text-accent-muted leading-relaxed mb-3">
          Unlock advanced features, more AI models &amp; higher limits.
        </p>
<button class="w-full py-1.5 px-3 bg-gradient-to-r from-ruby-600 to-accent-pink hover:from-ruby-500 hover:to-ruby-400 text-white rounded-xl text-xs font-semibold shadow-md shadow-ruby-900/40 flex items-center justify-center gap-1 transition-all" type="button">
<span class="">Upgrade Plan</span>
<span class="text-xs">→</span>
</button>
</div>
<!-- User Profile Card -->
<div class="relative z-10 flex items-center justify-between p-2 rounded-xl bg-wine-850/40 border border-wine-800/40 hover:bg-wine-800/40 transition cursor-pointer">
<div class="flex items-center gap-2.5">
<div class="w-8 h-8 rounded-full bg-gradient-to-tr from-ruby-700 to-accent-pink flex items-center justify-center text-white text-xs font-bold ring-2 ring-wine-900 shadow">
            VD
          </div>
<div class="leading-tight">
<h3 class="text-xs font-semibold text-white truncate w-24">Hriday Gupta</h3>
<p class="text-[10px] text-accent-muted truncate w-24">hriday.code1119@gmail.com</p>
</div>
</div>
<button aria-label="User menu" class="text-accent-muted hover:text-white p-1" type="button">
<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
<circle cx="5" cy="12" r="2"></circle><circle cx="12" cy="12" r="2"></circle><circle cx="19" cy="12" r="2"></circle>
</svg>
</button>
</div>
</div>
</aside>
<!-- END: SidebarNavigation -->
<!-- BEGIN: MainContentCanvas -->
<div class="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto bg-gradient-to-b from-wine-900 via-wine-900 to-[#12050c] relative" data-purpose="dashboard-main">
<!-- BEGIN: TopHeader -->
<header class="sticky top-0 z-30 h-16 bg-wine-900/85 backdrop-blur-md border-b border-wine-800/70 px-6 flex items-center justify-between gap-4 shrink-0">
<!-- Workspace Selector -->
<div class="flex items-center gap-3">
<button class="flex items-center gap-2 bg-wine-800/70 hover:bg-wine-750 text-xs font-medium text-white px-3.5 py-1.5 rounded-xl border border-wine-700/60 shadow-inner transition" type="button">
<svg class="w-3.5 h-3.5 text-accent-muted" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<path d="M3 21h18M3 10h18M5 10v11M19 10v11M9 10v11M15 10v11M12 2 2 7h20L12 2Z"></path>
</svg>
<span class="">Enterprise Workspace</span>
<svg class="w-3 h-3 text-accent-muted ml-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"></path></svg>
</button>
</div>
<!-- Omnibox / Search Prompt Command Bar -->
<div class="flex-1 max-w-xl mx-auto">
<div class="relative flex items-center">
<div class="absolute left-3.5 pointer-events-none text-accent-muted">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path>
</svg>
</div>
<input class="w-full bg-wine-950/60 border border-wine-800/90 rounded-2xl py-1.5 pl-10 pr-12 text-xs text-white placeholder-accent-muted focus:outline-none focus:border-ruby-500/80 focus:ring-1 focus:ring-ruby-500/80 shadow-inner" placeholder="Search or ask ENMA anything..." type="text">
<div class="absolute right-3 flex items-center">
<kbd class="px-1.5 py-0.5 text-[10px] font-semibold text-accent-muted bg-wine-800 rounded border border-wine-700 font-mono">⌘K</kbd>
</div>
</div>
</div>
<!-- Right Header Status & Actions -->
<div class="flex items-center gap-3">
<!-- Notification Bell with Active Indicator -->
<button aria-label="Notifications" class="relative p-2 text-accent-muted hover:text-white rounded-xl hover:bg-wine-800/60 transition" type="button">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path>
</svg>
<span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-ruby-500 ring-2 ring-wine-900"></span>
</button>
<!-- Small User Avatar -->
<div class="w-8 h-8 rounded-full bg-gradient-to-br from-ruby-600 to-accent-pink flex items-center justify-center text-white text-xs font-bold ring-2 ring-wine-800 shadow">
          VD
        </div>
</div>
</header>
<!-- END: TopHeader -->
<!-- BEGIN: DashboardBodyContent -->
<main class="p-6 space-y-6 flex-1 max-w-[1440px] w-full mx-auto pb-16">
<!-- BEGIN: HeroGreetingAndInput -->
<section class="relative rounded-2xl bg-gradient-to-r from-wine-850 via-[#2c0e1e] to-wine-800 border border-ruby-500/25 p-6 overflow-hidden shadow-xl" data-purpose="hero-banner">
<!-- Glowing Wave Accent Background -->
<div class="hero-wave"></div>
<!-- Top Wave Slogan & Accent -->
<div class="absolute right-8 top-5 select-none pointer-events-none hidden md:block">
<p class="font-handwriting text-2xl text-accent-soft/90 -rotate-3 tracking-wide drop-shadow-[0_2px_10px_rgba(244,63,118,0.5)]">
            Less manual work, more you. <span class="text-accent-pink">✦</span>
</p>
</div>
<div class="relative z-10 space-y-4">
<!-- Active Status Badge -->
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-wine-950/70 border border-wine-700/60 text-xs">
<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
<span class="text-white text-[11px] font-medium tracking-wide">ENMA is active</span>
</div>
<!-- Hero Greeting Headline -->
<div class="space-y-1">
<div class="flex items-center gap-2.5">
<span class="text-ruby-400 text-xl animate-pulse">✦</span>
<h2 class="text-2xl font-bold tracking-tight text-white">Hi Hriday— Good to see you!</h2>
</div>
<p class="text-xs text-accent-soft/80 max-w-2xl leading-relaxed">
              Your AI assistant is ready to help you get things done. Ask, automate, create, or just say what you need.
            </p>
</div>
<!-- Central Interactive AI Input Bar -->
<div class="mt-2 bg-wine-950/80 border border-wine-700/80 rounded-2xl p-1.5 pl-3.5 flex items-center gap-3 shadow-2xl focus-within:border-ruby-500/90 transition-all">
<span class="text-ruby-400 shrink-0">
<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
<path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"></path>
</svg>
</span>
<input class="flex-1 bg-transparent border-none text-xs text-white placeholder-accent-muted/70 focus:outline-none focus:ring-0 p-0" placeholder="Ask anything or enter a command (e.g. &quot;Send email to chetan@enterprise.com with project update&quot;)..." type="text">
<div class="flex items-center gap-1.5 pr-1">
<!-- Paperclip -->
<button class="p-1.5 text-accent-muted hover:text-white rounded-lg hover:bg-wine-800/60 transition" title="Attach file" type="button">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
</button>
<!-- Mic -->
<button class="p-1.5 text-accent-muted hover:text-white rounded-lg hover:bg-wine-800/60 transition" title="Voice command" type="button">
<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"></path></svg>
</button>
<!-- Submit / Run Prompt -->
<button class="p-2 bg-gradient-to-r from-ruby-600 to-accent-pink hover:from-ruby-500 hover:to-ruby-400 text-white rounded-xl shadow-md transition-transform hover:scale-105 active:scale-95" title="Run command" type="button">
<svg class="w-3.5 h-3.5 transform -rotate-45 ml-0.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
<path d="M5 12h14M12 5l7 7-7 7"></path>
</svg>
</button>
</div>
</div>
<!-- Quick Action Buttons Row -->
<div class="flex items-center gap-2 pt-1 overflow-x-auto text-xs pb-1" data-purpose="quick-actions">
<button class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-wine-950/60 hover:bg-wine-800 border border-wine-800/80 text-white transition shadow-sm whitespace-nowrap" type="button">
<span class="">✉️</span>
<span class="font-medium">Draft Email</span>
</button>
<button class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-wine-950/60 hover:bg-wine-800 border border-wine-800/80 text-white transition shadow-sm whitespace-nowrap" type="button">
<span class="">📄</span>
<span class="font-medium">Summarize Doc</span>
</button>
<button class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-wine-950/60 hover:bg-wine-800 border border-wine-800/80 text-white transition shadow-sm whitespace-nowrap" type="button">
<span class="">📅</span>
<span class="font-medium">Schedule Meeting</span>
</button>
<button class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-wine-950/60 hover:bg-wine-800 border border-wine-800/80 text-white transition shadow-sm whitespace-nowrap" type="button">
<span class="">📊</span>
<span class="font-medium">Analyze Data</span>
</button>
<button class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-wine-950/60 hover:bg-wine-800 border border-wine-800/80 text-accent-muted hover:text-white transition shadow-sm whitespace-nowrap ml-auto" type="button">
<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect height="7" rx="1" width="7" x="3" y="3"></rect><rect height="7" rx="1" width="7" x="14" y="3"></rect><rect height="7" rx="1" width="7" x="14" y="14"></rect><rect height="7" rx="1" width="7" x="3" y="14"></rect></svg>
<span class="">More</span>
<span class="text-[10px]">&gt;</span>
</button>
</div>
</div>
</section>
<!-- END: HeroGreetingAndInput -->
<!-- BEGIN: MetricsAndWidgetsGrid -->
<div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
<!-- LEFT 8 COLS: 3 Cards in a row (Tasks Progress, Productivity, AI Suggested) -->
<div class="lg:col-span-8 flex flex-col gap-5">
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
<!-- Card 1: AI Task Progress -->
<div class="bg-wine-850/70 border border-wine-800/80 rounded-2xl p-4 flex flex-col justify-between shadow-sm relative overflow-hidden" data-purpose="task-progress-card">
<div>
<div class="flex items-center justify-between text-xs font-semibold text-white mb-2">
<span class="flex items-center gap-1.5 text-ruby-400">
<svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
<span class="text-white">AI Task Progress</span>
</span>
<span class="text-accent-muted text-xs">&gt;</span>
</div>
<div class="flex items-center justify-between text-[11px] text-accent-muted mb-1.5">
<span class="flex items-center gap-1">
<span class="w-1.5 h-1.5 rounded-full bg-ruby-400"></span> Active Automations
                  </span>
<span class="font-semibold text-white">3/5</span>
</div>
<!-- Glowing Progress Bar -->
<div class="w-full h-1.5 bg-wine-950 rounded-full overflow-hidden mb-3">
<div class="h-full bg-gradient-to-r from-ruby-500 to-accent-pink rounded-full w-3/5 shadow-[0_0_8px_rgba(244,63,118,0.8)]"></div>
</div>
<!-- Checklist Items -->
<ul class="space-y-2 text-[11px]">
<li class="flex items-center gap-2 text-emerald-300">
<svg class="w-3.5 h-3.5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
<span class="text-accent-soft truncate">Processing 24 emails</span>
</li>
<li class="flex items-center gap-2 text-emerald-300">
<svg class="w-3.5 h-3.5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
<span class="text-accent-soft truncate">Summarizing client report</span>
</li>
<li class="flex items-center justify-between text-accent-soft gap-2">
<span class="flex items-center gap-2 truncate">
<span class="w-2 h-2 rounded-full bg-purple-500 animate-ping"></span>
<span class="truncate">Updating project tracker</span>
</span>
<span class="text-[9px] text-purple-300 bg-purple-950/60 border border-purple-800 px-1.5 py-0.5 rounded shrink-0">In progress</span>
</li>
<li class="flex items-center justify-between text-accent-muted gap-2">
<span class="flex items-center gap-2 truncate">
<span class="w-2 h-2 rounded-full bg-wine-700"></span>
<span class="truncate">Calendar sync</span>
</span>
<span class="text-[9px] text-accent-muted bg-wine-900 border border-wine-800 px-1.5 py-0.5 rounded shrink-0">Queued</span>
</li>
<li class="flex items-center justify-between text-accent-muted gap-2">
<span class="flex items-center gap-2 truncate">
<span class="w-2 h-2 rounded-full bg-wine-700"></span>
<span class="truncate">Document analysis</span>
</span>
<span class="text-[9px] text-accent-muted bg-wine-900 border border-wine-800 px-1.5 py-0.5 rounded shrink-0">Queued</span>
</li>
</ul>
</div>
</div>
<!-- Card 2: Productivity Snapshot -->
<div class="bg-wine-850/70 border border-wine-800/80 rounded-2xl p-4 flex flex-col justify-between shadow-sm" data-purpose="productivity-snapshot">
<div>
<div class="flex items-center justify-between text-xs font-semibold text-white mb-3">
<span class="flex items-center gap-1.5">
<span class="text-ruby-400">📊</span>
<span class="">Productivity Snapshot</span>
</span>
<button class="text-[10px] text-accent-muted hover:text-white flex items-center gap-1" type="button">
                    This Week <svg class="w-2.5 h-2.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"></path></svg>
</button>
</div>
<!-- 3 Metric Blocks -->
<div class="grid grid-cols-3 gap-2 text-center mb-3">
<div class="bg-wine-900/80 border border-wine-800/60 rounded-xl p-2 flex flex-col items-center justify-center">
<span class="text-ruby-400 text-xs mb-1">✉️</span>
<span class="text-sm font-bold text-white leading-tight">48</span>
<span class="text-[9px] text-accent-muted">Emails Sent</span>
<span class="text-[8px] text-emerald-400 font-semibold mt-0.5">↑ 12%</span>
</div>
<div class="bg-wine-900/80 border border-wine-800/60 rounded-xl p-2 flex flex-col items-center justify-center">
<span class="text-ruby-400 text-xs mb-1">☑️</span>
<span class="text-sm font-bold text-white leading-tight">15</span>
<span class="text-[9px] text-accent-muted">Tasks Done</span>
<span class="text-[8px] text-emerald-400 font-semibold mt-0.5">↑ 25%</span>
</div>
<div class="bg-wine-900/80 border border-wine-800/60 rounded-xl p-2 flex flex-col items-center justify-center">
<span class="text-ruby-400 text-xs mb-1">☕</span>
<span class="text-sm font-bold text-white leading-tight">6</span>
<span class="text-[9px] text-accent-muted">Meetings</span>
<span class="text-[8px] text-emerald-400 font-semibold mt-0.5">↑ 20%</span>
</div>
</div>
</div>
<!-- Quote Footer -->
<div class="bg-wine-950/60 rounded-xl p-2 text-center border border-wine-800/40">
<p class="text-[10px] text-accent-soft italic">
<span class="text-ruby-400 not-italic">✦</span> "Consistency builds momentum."
                </p>
</div>
</div>
<!-- Card 3: AI Suggested Next -->
<div class="bg-wine-850/70 border border-wine-800/80 rounded-2xl p-4 flex flex-col justify-between shadow-sm" data-purpose="ai-suggested-card">
<div>
<div class="flex items-center justify-between text-xs font-semibold text-white mb-3">
<span class="flex items-center gap-1.5">
<span class="text-ruby-400">✦</span>
<span class="">AI Suggested Next</span>
</span>
<span class="w-4 h-4 rounded-full bg-ruby-600/60 border border-ruby-500 text-[10px] flex items-center justify-center text-white font-bold">3</span>
</div>
<div class="space-y-2">
<a class="block p-2 rounded-xl bg-wine-900/80 border border-wine-800/60 hover:border-ruby-500/50 transition group" href="#">
<div class="flex items-center justify-between gap-2">
<div class="flex items-center gap-2">
<span class="text-xs text-ruby-400">📝</span>
<p class="text-[11px] text-white group-hover:text-ruby-300 line-clamp-1 font-medium">Summarize today's meeting notes</p>
</div>
<span class="text-[10px] text-accent-muted group-hover:text-white">&gt;</span>
</div>
<span class="text-[9px] text-accent-muted ml-5 block">from 11 AM</span>
</a>
<a class="block p-2 rounded-xl bg-wine-900/80 border border-wine-800/60 hover:border-ruby-500/50 transition group" href="#">
<div class="flex items-center justify-between gap-2">
<div class="flex items-center gap-2">
<span class="text-xs text-ruby-400">✉️</span>
<p class="text-[11px] text-white group-hover:text-ruby-300 line-clamp-1 font-medium">Follow up with client on proposal</p>
</div>
<span class="text-[10px] text-accent-muted group-hover:text-white">&gt;</span>
</div>
<span class="text-[9px] text-accent-muted ml-5 block">pending proposal</span>
</a>
<a class="block p-2 rounded-xl bg-wine-900/80 border border-wine-800/60 hover:border-ruby-500/50 transition group" href="#">
<div class="flex items-center justify-between gap-2">
<div class="flex items-center gap-2">
<span class="text-xs text-ruby-400">📈</span>
<p class="text-[11px] text-white group-hover:text-ruby-300 line-clamp-1 font-medium">Prepare weekly progress report</p>
</div>
<span class="text-[10px] text-accent-muted group-hover:text-white">&gt;</span>
</div>
<span class="text-[9px] text-accent-muted ml-5 block">(using last 7 days data)</span>
</a>
</div>
</div>
</div>
</div>
<!-- BEGIN: BottomEmailStudioSection (Inside 8 cols) -->
<div class="bg-wine-850/60 border border-wine-800/80 rounded-2xl p-5 shadow-lg space-y-4" data-purpose="email-studio-templates">
<!-- Header of Email Studio -->
<div class="flex items-center justify-between border-b border-wine-800/60 pb-3">
<div class="flex items-center gap-2">
<span class="text-ruby-400">✉️</span>
<h3 class="text-sm font-bold text-white">Email Studio &amp; Templates</h3>
</div>
<button class="px-2.5 py-1 rounded-lg bg-ruby-600/30 hover:bg-ruby-600/50 border border-ruby-500/60 text-ruby-200 text-xs font-semibold flex items-center gap-1 transition" type="button">
<span class="">+ New</span>
</button>
</div>
<!-- Sub Tabs -->
<div class="flex items-center gap-4 text-xs font-medium border-b border-wine-800/40 pb-2">
<button class="text-white border-b-2 border-ruby-500 pb-1.5 font-semibold" type="button">Templates</button>
<button class="text-accent-muted hover:text-white pb-1.5" type="button">Automation Toolkits</button>
<button class="text-accent-muted hover:text-white pb-1.5" type="button">Command Center Logs</button>
</div>
<!-- Popular Templates Grid -->
<div>
<div class="flex items-center justify-between mb-2">
<span class="text-[11px] font-semibold text-accent-muted uppercase tracking-wider">Popular Templates</span>
</div>
<div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
<!-- Template 1 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">📅</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">Meeting Request</p>
<p class="text-[10px] text-accent-muted truncate">Schedule a meeting</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
<!-- Template 2 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">📄</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">Leave Application</p>
<p class="text-[10px] text-accent-muted truncate">HR &amp; leave</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
<!-- Template 3 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">📈</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">Project Status</p>
<p class="text-[10px] text-accent-muted truncate">Update stakeholders</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
<!-- Template 4 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">🎓</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">BTech Major Project</p>
<p class="text-[10px] text-accent-muted truncate">Academic / Project</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
<!-- Template 5 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">🚀</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">Client Proposal</p>
<p class="text-[10px] text-accent-muted truncate">Business</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
<!-- Template 6 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">⚠️</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">Urgent Alert</p>
<p class="text-[10px] text-accent-muted truncate">Important / Escalation</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
<!-- Template 7 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">📋</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">Document Review</p>
<p class="text-[10px] text-accent-muted truncate">Feedback / Review</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
<!-- Template 8 -->
<div class="p-2.5 bg-wine-900/80 hover:bg-wine-800/80 border border-wine-800/60 hover:border-ruby-500/40 rounded-xl transition cursor-pointer flex items-center justify-between">
<div class="flex items-center gap-2 truncate">
<span class="text-base shrink-0">👥</span>
<div class="truncate leading-tight">
<p class="text-xs font-medium text-white truncate">Weekly Sync Agenda</p>
<p class="text-[10px] text-accent-muted truncate">Team sync</p>
</div>
</div>
<span class="text-[10px] text-accent-muted ml-1">&gt;</span>
</div>
</div>
</div>
<!-- Email Composer Form Section -->
<div class="pt-2 border-t border-wine-800/60" data-purpose="email-composer-form">
<!-- Mode Tabs -->
<div class="flex items-center gap-4 text-xs font-medium mb-3">
<button class="flex items-center gap-1.5 text-ruby-400 font-semibold border-b border-ruby-500 pb-1" type="button">
<span class="">✦</span> Compose &amp; AI Assistant
                </button>
<button class="flex items-center gap-1.5 text-accent-muted hover:text-white pb-1" type="button">
<span class="">&lt;/&gt;</span> Live HTML Preview
                </button>
</div>
<!-- Input Fields Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
<div>
<label class="block text-[11px] font-medium text-accent-soft mb-1">Recipient Email Address(es)*</label>
<input class="w-full bg-wine-950/80 border border-wine-800 rounded-xl py-1.5 px-3 text-xs text-accent-muted focus:text-white focus:outline-none focus:border-ruby-500" type="text" value="e.g., hriday.code1119@gmail.com, chetan@enterprise.com">
</div>
<div>
<label class="block text-[11px] font-medium text-accent-soft mb-1">Provider*</label>
<select class="w-full bg-wine-950/80 border border-wine-800 rounded-xl py-1.5 px-3 text-xs text-white focus:outline-none focus:border-ruby-500">
<option>Resend Email API</option>
<option>SendGrid Mail Engine</option>
<option>Amazon SES</option>
</select>
</div>
</div>
<!-- Subject Line & Notes -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
<div>
<label class="block text-[11px] font-medium text-accent-soft mb-1">Subject Line*</label>
<input class="w-full bg-wine-950/80 border border-wine-800 rounded-xl py-1.5 px-3 text-xs text-accent-muted focus:text-white focus:outline-none focus:border-ruby-500" type="text" value="e.g., Meeting Request: Sprint Review &amp; Architecture Sync">
</div>
<div>
<label class="block text-[11px] font-medium text-accent-soft mb-1 flex items-center gap-1">
<span class="text-ruby-400">✍️</span> Use rough notes below, then click to auto-expand into a polished email.
                  </label>
<textarea class="w-full bg-wine-950/80 border border-wine-800 rounded-xl py-1.5 px-3 text-xs text-accent-muted focus:text-white placeholder-accent-muted/60 focus:outline-none focus:border-ruby-500 resize-none" placeholder="Type your message or rough notes here (e.g., &quot;I want to schedule meeting with team tomorrow at 3pm&quot;)..." rows="2"></textarea>
</div>
</div>
<!-- Form Action Buttons -->
<div class="flex items-center gap-3">
<button class="py-2 px-4 bg-gradient-to-r from-ruby-600 to-accent-pink hover:from-ruby-500 hover:to-ruby-400 text-white rounded-xl text-xs font-semibold shadow-md shadow-ruby-950 flex items-center gap-1.5 transition" type="button">
<span class="">✦</span>
<span class="">Write Full Email with AI</span>
</button>
<button class="py-2 px-3.5 bg-wine-900 hover:bg-wine-800 border border-wine-700/80 text-accent-muted hover:text-white rounded-xl text-xs font-medium flex items-center gap-1.5 transition" type="button">
<span class="text-ruby-400">✖</span>
<span class="">Enter</span>
</button>
</div>
</div>
</div>
<!-- END: BottomEmailStudioSection -->
</div>
<!-- RIGHT 4 COLS: Today's Schedule, Recent Activity, Voice Engine, System Health -->
<div class="lg:col-span-4 flex flex-col gap-4">
<!-- BEGIN: TodaysSchedule -->
<div class="bg-wine-850/70 border border-wine-800/80 rounded-2xl p-4 shadow-sm" data-purpose="schedule-card">
<div class="flex items-center justify-between text-xs font-semibold text-white mb-3">
<span class="flex items-center gap-1.5">
<span class="text-ruby-400">📅</span>
<span class="">Today's Schedule</span>
</span>
<a class="text-[10px] text-accent-muted hover:text-white flex items-center gap-1" href="#">
                View Calendar →
              </a>
</div>
<!-- Schedule Items Timeline -->
<div class="space-y-3 relative before:absolute before:inset-0 before:left-2 before:w-0.5 before:bg-wine-800/50">
<!-- Item 1 (Live) -->
<div class="relative pl-6 flex items-start justify-between gap-2">
<span class="absolute left-1 top-1.5 w-2.5 h-2.5 rounded-full bg-emerald-400 ring-4 ring-wine-900"></span>
<div>
<span class="text-[10px] font-mono text-accent-muted block">09:00 AM</span>
<p class="text-xs font-semibold text-white leading-tight">Daily Engineering Standup</p>
<p class="text-[10px] text-accent-muted">30 mins · Team sync</p>
</div>
<span class="px-2 py-0.5 text-[9px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-full shrink-0">Live</span>
</div>
<!-- Item 2 -->
<div class="relative pl-6 flex items-start justify-between gap-2">
<span class="absolute left-1 top-1.5 w-2.5 h-2.5 rounded-full bg-ruby-400 ring-4 ring-wine-900"></span>
<div>
<span class="text-[10px] font-mono text-accent-muted block">11:00 AM</span>
<p class="text-xs font-semibold text-white leading-tight">Sprint Planning &amp; Architecture Sync</p>
<p class="text-[10px] text-accent-muted">1 hour · Google Meet</p>
</div>
<span class="px-2 py-0.5 text-[9px] font-semibold bg-wine-900 text-accent-muted border border-wine-800 rounded-full shrink-0">Upcoming</span>
</div>
<!-- Item 3 -->
<div class="relative pl-6 flex items-start justify-between gap-2">
<span class="absolute left-1 top-1.5 w-2.5 h-2.5 rounded-full bg-wine-700 ring-4 ring-wine-900"></span>
<div>
<span class="text-[10px] font-mono text-accent-muted block">02:00 PM</span>
<p class="text-xs font-semibold text-white leading-tight">Client Demonstration</p>
<p class="text-[10px] text-accent-muted">1 hour · Live feature walk</p>
</div>
<span class="px-2 py-0.5 text-[9px] font-semibold bg-wine-900 text-accent-muted border border-wine-800 rounded-full shrink-0">Upcoming</span>
</div>
<!-- Item 4 -->
<div class="relative pl-6 flex items-start justify-between gap-2">
<span class="absolute left-1 top-1.5 w-2.5 h-2.5 rounded-full bg-wine-700 ring-4 ring-wine-900"></span>
<div>
<span class="text-[10px] font-mono text-accent-muted block">04:30 PM</span>
<p class="text-xs font-semibold text-white leading-tight">Review &amp; Deliverables Wrap-up</p>
<p class="text-[10px] text-accent-muted">30 mins · Summary</p>
</div>
<span class="px-2 py-0.5 text-[9px] font-semibold bg-wine-900 text-accent-muted border border-wine-800 rounded-full shrink-0">Upcoming</span>
</div>
</div>
</div>
<!-- END: TodaysSchedule -->
<!-- BEGIN: RecentActivity -->
<div class="bg-wine-850/70 border border-wine-800/80 rounded-2xl p-4 shadow-sm" data-purpose="recent-activity-card">
<div class="flex items-center justify-between text-xs font-semibold text-white mb-3">
<span class="flex items-center gap-1.5">
<span class="text-ruby-400">🕒</span>
<span class="">Recent Activity</span>
</span>
<a class="text-[10px] text-accent-muted hover:text-white flex items-center gap-1" href="#">
                View All →
              </a>
</div>
<div class="space-y-3 text-[11px]">
<!-- Event 1 -->
<div class="flex items-start justify-between gap-2 border-b border-wine-800/30 pb-2">
<div class="flex items-start gap-2">
<span class="w-2 h-2 rounded-full bg-emerald-400 mt-1 shrink-0"></span>
<div>
<p class="font-semibold text-white leading-tight">Email dispatched to Chetan</p>
<p class="text-[10px] text-accent-muted">Project update and next steps</p>
</div>
</div>
<span class="text-[9px] font-mono text-accent-muted shrink-0">10:30 AM</span>
</div>
<!-- Event 2 -->
<div class="flex items-start justify-between gap-2 border-b border-wine-800/30 pb-2">
<div class="flex items-start gap-2">
<span class="w-2 h-2 rounded-full bg-purple-400 mt-1 shrink-0"></span>
<div>
<p class="font-semibold text-white leading-tight">Document summary synthesized</p>
<p class="text-[10px] text-accent-muted">Q1_Report.pdf (4 takeaways)</p>
</div>
</div>
<span class="text-[9px] font-mono text-accent-muted shrink-0">09:15 AM</span>
</div>
<!-- Event 3 -->
<div class="flex items-start justify-between gap-2 border-b border-wine-800/30 pb-2">
<div class="flex items-start gap-2">
<span class="w-2 h-2 rounded-full bg-amber-400 mt-1 shrink-0"></span>
<div>
<p class="font-semibold text-white leading-tight">Meeting scheduled</p>
<p class="text-[10px] text-accent-muted">Team sync on 24 May, 11:00 AM</p>
</div>
</div>
<span class="text-[9px] font-mono text-accent-muted shrink-0">09:00 AM</span>
</div>
<!-- Event 4 -->
<div class="flex items-start justify-between gap-2">
<div class="flex items-start gap-2">
<span class="w-2 h-2 rounded-full bg-blue-400 mt-1 shrink-0"></span>
<div>
<p class="font-semibold text-white leading-tight">Data extracted from sales.xlsx</p>
<p class="text-[10px] text-accent-muted">5 tables &amp; 2 charts generated</p>
</div>
</div>
<span class="text-[9px] font-mono text-accent-muted shrink-0">Yesterday</span>
</div>
</div>
</div>
<!-- END: RecentActivity -->
<!-- BEGIN: VoiceCommandEngine -->
<div class="bg-wine-850/70 border border-wine-800/80 rounded-2xl p-4 shadow-sm text-center relative overflow-hidden" data-purpose="voice-command-engine">
<div class="flex items-center justify-between text-xs font-semibold text-white mb-2">
<span class="flex items-center gap-1.5">
<svg class="w-4 h-4 text-ruby-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"></path></svg>
<span class="">Voice Command Engine</span>
</span>
<span class="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[9px] font-medium flex items-center gap-1">
<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Listening
              </span>
</div>
<!-- Soundwave visualizer graphic -->
<div class="h-10 flex items-center justify-center gap-1.5 my-2">
<span class="w-1 bg-ruby-400 rounded-full wave-bar" style="height: 12px"></span>
<span class="w-1 bg-ruby-500 rounded-full wave-bar" style="height: 22px"></span>
<span class="w-1 bg-accent-pink rounded-full wave-bar" style="height: 18px"></span>
<span class="w-1 bg-ruby-400 rounded-full wave-bar" style="height: 30px"></span>
<span class="w-1 bg-ruby-500 rounded-full wave-bar" style="height: 14px"></span>
<span class="w-1 bg-accent-pink rounded-full wave-bar" style="height: 26px"></span>
<span class="w-1 bg-ruby-400 rounded-full wave-bar" style="height: 20px"></span>
<span class="w-1 bg-ruby-500 rounded-full wave-bar" style="height: 16px"></span>
<span class="w-1 bg-accent-pink rounded-full wave-bar" style="height: 28px"></span>
<span class="w-1 bg-ruby-400 rounded-full wave-bar" style="height: 10px"></span>
</div>
<p class="text-[10px] text-accent-muted mb-3">Tap to speak or say "Hey ENMA"</p>
<!-- Circular Mic Button -->
<button aria-label="Activate voice" class="w-10 h-10 mx-auto rounded-full bg-gradient-to-tr from-ruby-600 to-accent-pink hover:scale-105 active:scale-95 text-white flex items-center justify-center shadow-lg shadow-ruby-900/50 transition" type="button">
<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
<path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"></path>
<path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"></path>
</svg>
</button>
</div>
<!-- END: VoiceCommandEngine -->
<!-- BEGIN: SystemStatusCard -->
<div class="relative bg-wine-850/80 border border-wine-800/80 rounded-2xl p-3.5 flex items-center justify-between overflow-hidden shadow-sm" data-purpose="workspace-status">
<!-- Fluid wave glow accent on bottom right of the entire board -->
<div class="footer-wave"></div>
<div class="flex items-center gap-2.5 relative z-10">
<span class="text-base text-emerald-400">🌱</span>
<div class="leading-tight">
<p class="text-xs font-semibold text-white">Your workspace is running smoothly</p>
<p class="text-[10px] text-accent-muted">All systems operational · 99.9% uptime</p>
</div>
</div>
<span class="text-accent-muted text-xs relative z-10">&gt;</span>
</div>
<!-- END: SystemStatusCard -->
</div>
</div>
<!-- END: MetricsAndWidgetsGrid -->
</main>
<!-- END: DashboardBodyContent -->
</div>
<!-- END: MainContentCanvas -->



<script>
    const templates = {
        'Meeting Request': {
            subject: 'Meeting Request: Sprint Review & Architecture Sync',
            body: 'Dear Team,\n\nI would like to schedule a project sync meeting to discuss our upcoming deliverables.\n\nProposed Time: Tomorrow at 3:00 PM IST (Google Meet)\n\nBest regards,\nENMA Project Team'
        },
        'Leave Application': {
            subject: 'Leave Application: Request for Absence',
            body: 'Dear Team Lead,\n\nI am writing to formally request leave from [Start Date] to [End Date] due to personal commitments.\n\nThank you,\n[Your Name]'
        },
        'Project Status': {
            subject: '[Update] Project Status Report: Milestones Completed',
            body: 'Hi Team,\n\nHere is our project progress report:\n• Completed: AI Core, Multi-Format Document Studio, and Supabase integration.\n• Tests: 100% automated test coverage.\n\nBest regards,\nProject Team'
        },
        'BTech Major Project': {
            subject: 'BTech Major Project: Bi-Weekly Progress Submission',
            body: 'Respected Advisor,\n\nPlease find attached our progress report for the Autonomous AI Agent project.\nTeam: Hriday Gupta (Lead), Chetan.\nAll benchmarks achieved 100% accuracy.\n\nSincerely,\nProject Team'
        },
        'Client Proposal': {
            subject: 'Partnership Proposal: Autonomous Task Automation Solutions',
            body: 'Dear Client,\n\nThank you for your interest in our enterprise automation solutions.\nWe would love to demonstrate a 15-minute live demo this week.\n\nBest regards,\nBusiness Development Team'
        },
        'Urgent Alert': {
            subject: 'URGENT: Production Alert & Immediate Action Required',
            body: 'Hello Team,\n\nThis is an automated high-priority alert regarding task pipeline execution.\nPlease review system logs immediately.\n\nThank you,\nENMA Monitoring System'
        },
        'Document Review': {
            subject: 'Document Review: System Architecture & Technical Specifications',
            body: 'Hi Team,\n\nI have updated technical documentation for our AI automation platform.\nKindly review and submit comments by tomorrow.\n\nBest regards,\nEngineering Lead'
        },
        'Weekly Sync Agenda': {
            subject: 'Agenda: Weekly Engineering Sprint Sync & Milestone Planning',
            body: 'Dear Colleagues,\n\nPlease find proposed agenda for our upcoming weekly engineering sync:\n1. Sprint retrospectives.\n2. Live demonstration.\n\nBest regards,\nProject Coordinator'
        }
    };

    function loadTemplate(key) {
        const t = templates[key];
        if (!t) return;
        const subInput = document.querySelector('input[value*="Meeting Request"]') || document.querySelectorAll('input[type="text"]')[2];
        if (subInput) subInput.value = t.subject;
        const bodyTextarea = document.querySelector('textarea');
        if (bodyTextarea) bodyTextarea.value = t.body;
    }

    // Attach click listeners to template buttons
    document.addEventListener('DOMContentLoaded', () => {
        const tmplDivs = document.querySelectorAll('[data-purpose="email-studio-templates"] .grid > div');
        tmplDivs.forEach(div => {
            const titleEl = div.querySelector('p.font-medium');
            if (titleEl) {
                const title = titleEl.innerText.trim();
                div.addEventListener('click', () => loadTemplate(title));
            }
        });
    });
</script>

</body></html>"""
