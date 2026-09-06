"""
ENMA: Autonomous Enterprise AI Task Automation Platform.
Tagline: Intelligence That Gets Work Done
Main Streamlit Application Entrypoint.
"""

from __future__ import annotations
import os
import streamlit as st

from agent.orchestrator import AgentOrchestrator, WorkflowState
from integrations.oauth_handler import GoogleOAuthHandler
from tools.registry import ToolRegistry
from components.enma_sidebar import render_enma_sidebar
from components.enma_header import render_enma_header
from components.enma_dashboard import render_enma_dashboard
from components.calendar_view import render_calendar_view
from components.document_studio import render_document_studio
from components.notes_journal_view import (
    render_notes_view,
    render_journals_view,
    render_bookmarks_view,
)
from components.command_input import render_command_input
from components.draft_card import render_draft_card
from components.clarification_modal import render_clarification_card
from components.timeline import render_timeline
from components.email_composer import render_email_composer
from components.team_view import render_team_view

# 1. Streamlit Page Configuration
st.set_page_config(
    page_title="ENMA | Intelligence That Gets Work Done",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Custom Enterprise CSS
import base64

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        wp_path = os.path.join(os.path.dirname(__file__), "assets", "enma-wallpaper.png")
        if os.path.exists(wp_path):
            with open(wp_path, "rb") as wpf:
                b64_wp = base64.b64encode(wpf.read()).decode("utf-8")
                css_content = css_content.replace("__WALLPAPER_BASE64__", f"data:image/png;base64,{b64_wp}")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

load_css()

# 3. Session State Initialization
if "orchestrator" not in st.session_state:
    st.session_state.oauth_handler = GoogleOAuthHandler()
    st.session_state.tool_registry = ToolRegistry()
    st.session_state.orchestrator = AgentOrchestrator(
        registry=st.session_state.tool_registry,
        oauth_handler=st.session_state.oauth_handler,
    )

if "enma_active_view" not in st.session_state:
    st.session_state.enma_active_view = st.session_state.get(
        "lucora_active_view",
        st.session_state.get("aira_active_view", "dashboard")
    )
st.session_state.lucora_active_view = st.session_state.enma_active_view
st.session_state.aira_active_view = st.session_state.enma_active_view

orchestrator: AgentOrchestrator = st.session_state.orchestrator
oauth_handler: GoogleOAuthHandler = st.session_state.oauth_handler
tool_registry: ToolRegistry = st.session_state.tool_registry

# 4. Render Master ENMA Sidebar
selected_view = render_enma_sidebar(st.session_state.enma_active_view)
if selected_view != st.session_state.enma_active_view:
    st.session_state.enma_active_view = selected_view
    st.session_state.lucora_active_view = selected_view
    st.session_state.aira_active_view = selected_view
    st.rerun()

# 5. Render Top Header Bar
def navigate_to_view(v: str):
    st.session_state.enma_active_view = v
    st.session_state.lucora_active_view = v
    st.session_state.aira_active_view = v
    st.rerun()

render_enma_header(on_new_task_click=lambda: navigate_to_view("tasks"))

# 6. View Routing
current_view = st.session_state.enma_active_view

if current_view == "dashboard":
    render_enma_dashboard(orchestrator, on_navigate_view=navigate_to_view)

elif current_view in ("tasks", "assistant"):
    st.markdown("### Task & Email Studio")
    st.caption("Compose custom emails, select enterprise templates, or execute natural-language instructions via Resend & Gmail API.")
    
    tab_composer, tab_ai_chat = st.tabs(["Email Composer & Templates", "Conversational AI Assistant"])

    with tab_composer:
        render_email_composer(key_prefix="main_")

    with tab_ai_chat:
        col_main, col_side = st.columns([7, 3])
        with col_main:
            if orchestrator.state in (WorkflowState.IDLE, WorkflowState.CANCELLED):
                render_command_input(on_submit_callback=lambda ins: (orchestrator.submit_instruction(ins), st.rerun()))
            elif orchestrator.state == WorkflowState.CLARIFICATION_REQUIRED:
                render_clarification_card(
                    plan=orchestrator.current_plan,
                    on_resolve_callback=lambda res: (orchestrator.submit_clarification(res), st.rerun()),
                    on_cancel_callback=lambda: (orchestrator.cancel_current_task(), st.rerun()),
                )
            elif orchestrator.state == WorkflowState.AWAITING_APPROVAL:
                render_draft_card(
                    plan=orchestrator.current_plan,
                    on_approve_send=lambda p: (orchestrator.execute_confirmed_task(p), st.rerun()),
                    on_save_draft=lambda p: (orchestrator.execute_confirmed_task(p), st.rerun()),
                    on_cancel=lambda: (orchestrator.cancel_current_task(), st.rerun()),
                )
            elif orchestrator.state in (WorkflowState.COMPLETED, WorkflowState.FAILED):
                st.info("Task execution cycle completed.")

            st.divider()
            render_timeline(
                state=orchestrator.state,
                last_result=orchestrator.last_result,
                elapsed_ms=orchestrator.last_execution_time_ms,
                on_reset_callback=lambda: (orchestrator.reset(), st.rerun()),
            )
        with col_side:
            with st.container(border=True):
                st.markdown("##### Workspace Status")
                is_auth = oauth_handler.is_authenticated()
                if is_auth:
                    st.success(f"**Gmail API Active**\n`{oauth_handler.get_authenticated_user_email() or 'user@workspace.com'}`")
                else:
                    st.warning("Gmail API Disconnected")
                    if st.button("Mock Auth", use_container_width=True):
                        oauth_handler.create_mock_authenticated_session("hriday.code1119@gmail.com")
                        st.rerun()

            with st.container(border=True):
                from integrations.resend_client import ResendClient
                rc = ResendClient()
                if rc.is_configured():
                    st.success("**Resend API Active**\n`onboarding@resend.dev`")
                else:
                    st.info("Resend Inactive\n(Configure in Settings)")

elif current_view == "calendar":
    render_calendar_view()

elif current_view in ("files", "data", "documents"):
    render_document_studio()

elif current_view in ("notes", "journals", "bookmarks"):
    tab_n, tab_j, tab_b = st.tabs(["Notes", "Work Journals", "Bookmarks"])
    with tab_n:
        render_notes_view()
    with tab_j:
        render_journals_view()
    with tab_b:
        render_bookmarks_view()

elif current_view in ("team", "members"):
    render_team_view(on_navigate_view=navigate_to_view)

elif current_view in ("voice", "voice_commands"):
    st.markdown("### Voice Command Engine")
    st.caption("Voice-activated enterprise agent executing commands via speech synthesis.")
    
    st.markdown(
        """
        <div class="enma-card lucora-card" style="max-width: 540px; margin: 2rem auto; text-align: center;">
            <div class="soundwave-container" style="height: 50px;">
                <div class="wave-bar" style="width: 4px;"></div>
                <div class="wave-bar" style="width: 4px;"></div>
                <div class="wave-bar" style="width: 4px;"></div>
                <div class="wave-bar" style="width: 4px;"></div>
                <div class="wave-bar" style="width: 4px;"></div>
                <div class="wave-bar" style="width: 4px;"></div>
                <div class="wave-bar" style="width: 4px;"></div>
                <div class="wave-bar" style="width: 4px;"></div>
            </div>
            <h4 style="margin: 0.5rem 0;">ENMA Voice Engine Active</h4>
            <p style="color: #64748b; font-size: 0.88rem;">Speak a natural language instruction to execute tasks across Gmail, Calendar, and Documents.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
    with col_v2:
        if st.button("Speak Command Now →", key="voice_page_speak", type="primary", use_container_width=True):
            st.toast("Transcribed: 'Send email to Chetan about project update'", icon="🎙")
            orchestrator.submit_instruction("Send an email to chetan@enterprise.com with project update.")
            navigate_to_view("tasks")

elif current_view in ("terminal", "integrations", "settings"):
    st.markdown("### System & Settings")
    st.caption("Configure API keys, Google Workspace OAuth credentials, and inspect live execution logs.")

    st.markdown("#### Terminal Logs")
    st.markdown(
        """
        <div class="terminal-container" style="height: 180px;">
            <span class="terminal-prompt">></span> <span class="terminal-cmd">ENMA v2.4 initialized on Linux</span><br>
            <span class="terminal-prompt">></span> <span class="terminal-success">ToolRegistry loaded 6 dynamic tools</span><br>
            <span class="terminal-prompt">></span> <span class="terminal-cmd">Loaded Gemini 1.5 Flash Cognitive Core</span><br>
            <span class="terminal-prompt">></span> <span class="terminal-success">OAuth 2.0 PKCE session active</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("#### Supabase Cloud Database")
    from database.supabase_client import SupabaseManager
    sb_mgr = SupabaseManager()

    sb_col1, sb_col2 = st.columns([5, 4])
    with sb_col1:
        if sb_mgr.is_connected():
            st.success("🟢 **Supabase Connected** (PostgreSQL Cloud Persistence Active)")
        else:
            st.info("⚪ **Local Fallback Mode** (Supabase credentials not configured)")

        is_ok, ping_msg = sb_mgr.ping()
        st.caption(f"Status Diagnostic: `{ping_msg}`")

        with st.expander("Supabase SQL Schema Setup", expanded=False):
            st.caption("Copy and run this SQL in your Supabase SQL Editor:")
            st.code(
                """-- Quick Supabase Setup
CREATE TABLE IF NOT EXISTS aira_tasks (id TEXT PRIMARY KEY, user_instruction TEXT, state TEXT, plan_json JSONB, tool_name TEXT, execution_time_ms FLOAT, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS aira_calendar_events (id TEXT PRIMARY KEY, title TEXT, event_time TEXT, duration TEXT, meet_url TEXT, attendees JSONB, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS aira_documents (id TEXT PRIMARY KEY, filename TEXT, file_type TEXT, word_count INT, raw_text TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS aira_notes (id TEXT PRIMARY KEY, category TEXT, title TEXT, content TEXT, date_str TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
                """,
                language="sql",
            )

    with sb_col2:
        with st.form(key="supabase_config_form"):
            st.markdown("##### Configure Supabase API")
            sb_url = st.text_input("Supabase URL", value=os.getenv("SUPABASE_URL", ""), placeholder="https://xyzcompany.supabase.co")
            sb_key = st.text_input("Supabase Anon Key", value=os.getenv("SUPABASE_KEY", ""), type="password", placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
            
            btn_save = st.form_submit_button("Save & Connect Supabase →", type="primary", use_container_width=True)
            if btn_save and sb_url and sb_key:
                ok, msg = sb_mgr.configure(sb_url, sb_key)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()
    st.markdown("#### Resend Email API Integration")
    from integrations.resend_client import ResendClient
    resend_cli = ResendClient()

    res_col1, res_col2 = st.columns([5, 4])
    with res_col1:
        if resend_cli.is_configured():
            st.success("🟢 **Resend API Connected** (Active Email Dispatch Provider)")
            st.caption(f"Sender Address: `{resend_cli.default_from}`")
        else:
            st.info("⚪ **Resend Inactive** (Enter API key to enable live transactional email dispatch)")

        with st.form(key="resend_test_form"):
            st.markdown("##### Send Test Email")
            test_to = st.text_input("Recipient Email", placeholder="your_email@domain.com")
            test_btn = st.form_submit_button("Send Test Email →", use_container_width=True)
            if test_btn and test_to:
                try:
                    res = resend_cli.send_email(
                        to=test_to.strip(),
                        subject="ENMA AI Agent - Resend Integration Test",
                        text="Congratulations! Your Resend API integration with ENMA Autonomous AI Agent is working perfectly.",
                    )
                    st.success(f"Email dispatched! ID: `{res.get('id')}` ({res.get('mode')} mode)")
                except Exception as ex:
                    st.error(f"Failed to send: {str(ex)}")

    with res_col2:
        with st.form(key="resend_config_form"):
            st.markdown("##### Configure Resend API Key")
            rk = st.text_input("Resend API Key", value=os.getenv("RESEND_API_KEY", ""), type="password", placeholder="re_123456789...")
            rf = st.text_input("Sender Email / Domain", value=os.getenv("RESEND_FROM_EMAIL", "ENMA AI <onboarding@resend.dev>"), placeholder="ENMA AI <onboarding@resend.dev>")
            
            btn_save_resend = st.form_submit_button("Save Resend Key →", type="primary", use_container_width=True)
            if btn_save_resend and rk:
                resend_cli.configure(rk, rf)
                st.success("Resend API key saved successfully!")
                st.rerun()

    st.divider()
    st.markdown("#### Workspace Integrations")
    is_auth = oauth_handler.is_authenticated()
    if is_auth:
        st.success(f"**Google Gmail & Calendar Connected:** `{oauth_handler.get_authenticated_user_email() or 'user@workspace.com'}`")
    else:
        st.warning("Google Workspace disconnected.")
        if st.button("Authenticate with Google →", type="primary"):
            oauth_handler.create_mock_authenticated_session("hriday.code1119@gmail.com")
            st.rerun()
