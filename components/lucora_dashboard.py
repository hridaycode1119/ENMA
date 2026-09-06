"""
LUCORA Master Enterprise Dashboard Component.
Renders the complete multi-widget command center matching the reference UI design.
Brand tagline: "Intelligence That Gets Work Done"
"""

from __future__ import annotations
import streamlit as st
import datetime

from agent.orchestrator import AgentOrchestrator, WorkflowState
from components.draft_card import render_draft_card
from components.clarification_modal import render_clarification_card
from components.timeline import render_timeline
from components.email_composer import render_email_composer
from database.repository import LUCORARepository, AIRARepository

def _set_active_view(view_name: str) -> None:
    st.session_state["lucora_active_view"] = view_name
    st.session_state["aira_active_view"] = view_name

def render_lucora_dashboard(orchestrator: AgentOrchestrator, on_navigate_view) -> None:
    """Renders the complete 12-widget unified LUCORA AI Agent Dashboard."""
    
    repo = LUCORARepository()
    metrics = repo.get_task_metrics()

    # --------------------------------------------------------------------------
    # 1. Top KPI Summary Cards (5 Cards)
    # --------------------------------------------------------------------------
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-icon-wrapper" style="background: rgba(109, 40, 217, 0.1); color: #6d28d9;">✓</div>
                <div class="kpi-val">{metrics['completed']}</div>
                <div class="kpi-label">Tasks Completed</div>
                <div class="kpi-delta delta-purple">↑ 18% from yesterday</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-icon-wrapper" style="background: rgba(16, 185, 129, 0.1); color: #10b981;">✉</div>
                <div class="kpi-val">{metrics['emails_sent']}</div>
                <div class="kpi-label">Emails Sent</div>
                <div class="kpi-delta delta-green">↑ 24% from yesterday</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-icon-wrapper" style="background: rgba(245, 158, 11, 0.1); color: #f59e0b;">📅</div>
                <div class="kpi-val">{metrics['events_today']}</div>
                <div class="kpi-label">Events Today</div>
                <div class="kpi-delta delta-orange">1 upcoming</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col4:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-icon-wrapper" style="background: rgba(59, 130, 246, 0.1); color: #3b82f6;">📄</div>
                <div class="kpi-val">{metrics['files_processed']}</div>
                <div class="kpi-label">Files Processed</div>
                <div class="kpi-delta delta-blue">↑ 32% from yesterday</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col5:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-icon-wrapper" style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6;">⏱</div>
                <div class="kpi-val">{metrics['time_saved_hours']}h</div>
                <div class="kpi-label">Time Saved</div>
                <div class="kpi-delta delta-purple">This week</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --------------------------------------------------------------------------
    # 2. Middle 3-Column Workspace: Recent Activity | AI Assistant | Schedule
    # --------------------------------------------------------------------------
    mid_left, mid_center, mid_right = st.columns([3, 4, 3])

    # A. Recent Activity
    with mid_left:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">Recent Activity</div>
                    <span class="aira-card-link lucora-card-link">View All</span>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #ecfdf5; color: #10b981;">✉</div>
                    <div>
                        <div class="activity-title">Email sent to Chetan</div>
                        <div class="activity-sub">Project update and next steps</div>
                    </div>
                    <div class="activity-time">10:30 AM <span class="status-dot" style="background: #10b981;"></span></div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #eff6ff; color: #3b82f6;">📄</div>
                    <div>
                        <div class="activity-title">Document summary created</div>
                        <div class="activity-sub">Q1_Report.pdf</div>
                    </div>
                    <div class="activity-time">09:15 AM <span class="status-dot" style="background: #3b82f6;"></span></div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #fffbeb; color: #f59e0b;">📅</div>
                    <div>
                        <div class="activity-title">Meeting scheduled</div>
                        <div class="activity-sub">Team sync on 24 May, 11:00 AM</div>
                    </div>
                    <div class="activity-time">09:00 AM <span class="status-dot" style="background: #f59e0b;"></span></div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #f5f3ff; color: #7c3aed;">📊</div>
                    <div>
                        <div class="activity-title">Data extracted from sales.xlsx</div>
                        <div class="activity-sub">5 tables, 2 charts generated</div>
                    </div>
                    <div class="activity-time">Yesterday <span class="status-dot" style="background: #7c3aed;"></span></div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #ecfdf5; color: #10b981;">✓</div>
                    <div>
                        <div class="activity-title">Task completed</div>
                        <div class="activity-sub">Send proposal to client</div>
                    </div>
                    <div class="activity-time">Yesterday <span class="status-dot" style="background: #10b981;"></span></div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #fdf4ff; color: #c026d3;">🎙️</div>
                    <div>
                        <div class="activity-title">Voice command executed</div>
                        <div class="activity-sub">Create meeting notes</div>
                    </div>
                    <div class="activity-time">2 days ago <span class="status-dot" style="background: #3b82f6;"></span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # B. Central AI Assistant Interactive Hub
    with mid_center:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">✨ LUCORA AI Assistant</div>
                </div>
                <div class="ai-assistant-bubble">
                    <p><strong>Hi Vaishnavi! 👋 Welcome to LUCORA</strong><br><em>Intelligence That Gets Work Done</em>. How can I assist you today?</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick action chips
        chip_col1, chip_col2 = st.columns(2)
        with chip_col1:
            if st.button("📄 Summarize a document", key="lucora_chip_sum", use_container_width=True):
                _set_active_view("documents")
                st.rerun()
            if st.button("📊 Analyze data", key="lucora_chip_data", use_container_width=True):
                _set_active_view("documents")
                st.rerun()
        with chip_col2:
            if st.button("📅 Schedule a meeting", key="lucora_chip_meet", use_container_width=True):
                _set_active_view("calendar")
                st.rerun()
            if st.button("📝 Generate report", key="lucora_chip_rep", use_container_width=True):
                _set_active_view("documents")
                st.rerun()

        # Conversational Task Prompt Box
        with st.form(key="lucora_prompt_form"):
            user_prompt = st.text_input(
                "Command Prompt",
                placeholder="Ask anything or give a command (e.g., 'Send email to Chetan about project update')...",
                label_visibility="collapsed",
            )
            submit_prompt = st.form_submit_button("🚀 Send Command", type="primary", use_container_width=True)

            if submit_prompt and user_prompt.strip():
                with st.spinner("LUCORA reasoning over instruction..."):
                    orchestrator.submit_instruction(user_prompt.strip())
                st.rerun()

        # Bottom Feature Pills
        f_c1, f_c2, f_c3, f_c4 = st.columns(4)
        with f_c1:
            if st.button("✉️ Smart Reply", key="feat_reply", use_container_width=True):
                st.toast("Smart Reply loaded for email drafts", icon="✉️")
        with f_c2:
            if st.button("📑 File Insights", key="feat_insights", use_container_width=True):
                _set_active_view("documents")
                st.rerun()
        with f_c3:
            if st.button("✅ Task Planner", key="feat_planner", use_container_width=True):
                _set_active_view("tasks")
                st.rerun()
        with f_c4:
            if st.button("⚡ Workflow", key="feat_flow", use_container_width=True):
                _set_active_view("terminal")
                st.rerun()

        # If an action plan is active, render the HITL Review card inline!
        if orchestrator.state == WorkflowState.AWAITING_APPROVAL:
            st.divider()
            render_draft_card(
                plan=orchestrator.current_plan,
                on_approve_send=lambda p: (orchestrator.execute_confirmed_task(p), st.rerun()),
                on_save_draft=lambda p: (orchestrator.execute_confirmed_task(p), st.rerun()),
                on_cancel=lambda: (orchestrator.cancel_current_task(), st.rerun()),
            )
        elif orchestrator.state == WorkflowState.CLARIFICATION_REQUIRED:
            st.divider()
            render_clarification_card(
                plan=orchestrator.current_plan,
                on_resolve_callback=lambda res: (orchestrator.submit_clarification(res), st.rerun()),
                on_cancel_callback=lambda: (orchestrator.cancel_current_task(), st.rerun()),
            )
        elif orchestrator.state in (WorkflowState.COMPLETED, WorkflowState.FAILED):
            st.divider()
            render_timeline(
                state=orchestrator.state,
                last_result=orchestrator.last_result,
                elapsed_ms=orchestrator.last_execution_time_ms,
                on_reset_callback=lambda: (orchestrator.reset(), st.rerun()),
            )

    # C. Today's Schedule & Month Calendar
    with mid_right:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">Today's Schedule</div>
                    <span class="aira-card-link lucora-card-link">View Calendar</span>
                </div>
                <div class="schedule-item">
                    <div class="schedule-time">09:00 AM</div>
                    <div>
                        <div class="schedule-title">Daily Standup</div>
                        <div class="schedule-duration">30 mins</div>
                    </div>
                </div>
                <div class="schedule-item">
                    <div class="schedule-time">11:00 AM</div>
                    <div>
                        <div class="schedule-title">Team Sync</div>
                        <div class="schedule-duration">1 hour</div>
                    </div>
                </div>
                <div class="schedule-item">
                    <div class="schedule-time">02:00 PM</div>
                    <div>
                        <div class="schedule-title">Client Presentation</div>
                        <div class="schedule-duration">1 hour</div>
                    </div>
                </div>
                <div class="schedule-item">
                    <div class="schedule-time">04:30 PM</div>
                    <div>
                        <div class="schedule-title">Review & Planning</div>
                        <div class="schedule-duration">30 mins</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --------------------------------------------------------------------------
    # 2.5 Quick Email Automation & Template Studio
    # --------------------------------------------------------------------------
    with st.expander("✉️ **Quick Email Automation & AI Composer Studio**", expanded=True):
        render_email_composer(key_prefix="dash_")

    st.write("")

    # --------------------------------------------------------------------------
    # 3. Lower 4-Card Grid: Task Donut | File Manager | Quick Tools | Voice
    # --------------------------------------------------------------------------
    low_col1, low_col2, low_col3, low_col4 = st.columns(4)

    # A. Task Overview Donut Chart
    with low_col1:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">Task Overview</div>
                </div>
                <div style="text-align: center; margin: 0.8rem 0;">
                    <div style="font-size: 2.2rem; font-weight: 800; color: #6d28d9; line-height: 1;">43</div>
                    <div style="font-size: 0.76rem; color: #64748b; font-weight: 600;">Total Tasks</div>
                </div>
                <div style="font-size: 0.78rem; display: flex; flex-direction: column; gap: 0.35rem; margin-top: 0.6rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span><span style="color: #3b82f6;">●</span> To Do</span> <strong>12</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span><span style="color: #06b6d4;">●</span> In Progress</span> <strong>5</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span><span style="color: #10b981;">●</span> Completed</span> <strong>24</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span><span style="color: #ef4444;">●</span> Blocked</span> <strong>2</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # B. File Manager Card
    with low_col2:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">File Manager</div>
                    <span class="aira-card-link lucora-card-link">View All</span>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #fef2f2; color: #ef4444;">📄</div>
                    <div>
                        <div class="activity-title">Project_Proposal.pdf</div>
                        <div class="activity-sub">1.2 MB • PDF</div>
                    </div>
                    <div class="activity-time">10:20 AM</div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #ecfdf5; color: #10b981;">📊</div>
                    <div>
                        <div class="activity-title">Sales_Data.xlsx</div>
                        <div class="activity-sub">850 KB • Excel</div>
                    </div>
                    <div class="activity-time">Yesterday</div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #eff6ff; color: #3b82f6;">📝</div>
                    <div>
                        <div class="activity-title">Meeting_Notes.docx</div>
                        <div class="activity-sub">450 KB • Word</div>
                    </div>
                    <div class="activity-time">Yesterday</div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #fef2f2; color: #ef4444;">📄</div>
                    <div>
                        <div class="activity-title">Q1_Report.pdf</div>
                        <div class="activity-sub">2.1 MB • PDF</div>
                    </div>
                    <div class="activity-time">2 days ago</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # C. Quick Tools 2x4 Grid
    with low_col3:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">Quick Tools</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        qt_r1_c1, qt_r1_c2, qt_r1_c3, qt_r1_c4 = st.columns(4)
        with qt_r1_c1:
            if st.button("📄\nConv", key="qt_conv", use_container_width=True, help="File Converter"):
                _set_active_view("documents")
                st.rerun()
        with qt_r1_c2:
            if st.button("📑\nPDF", key="qt_pdf", use_container_width=True, help="PDF Editor"):
                _set_active_view("documents")
                st.rerun()
        with qt_r1_c3:
            if st.button("📊\nData", key="qt_data", use_container_width=True, help="Data Extractor"):
                _set_active_view("documents")
                st.rerun()
        with qt_r1_c4:
            if st.button("📈\nChart", key="qt_chart", use_container_width=True, help="Chart Generator"):
                st.toast("Chart Generator Ready", icon="📈")

        qt_r2_c1, qt_r2_c2, qt_r2_c3, qt_r2_c4 = st.columns(4)
        with qt_r2_c1:
            if st.button("🖼️\nOCR", key="qt_ocr", use_container_width=True, help="Image to Text"):
                st.toast("Image to Text OCR tool active", icon="🖼️")
        with qt_r2_c2:
            if st.button("🔗\nMerge", key="qt_merge", use_container_width=True, help="Merge Files"):
                _set_active_view("documents")
                st.rerun()
        with qt_r2_c3:
            if st.button("🗜️\nZip", key="qt_zip", use_container_width=True, help="Compress Files"):
                st.toast("File Compressor Active", icon="🗜️")
        with qt_r2_c4:
            if st.button("✨\nMore", key="qt_more", use_container_width=True, help="More Tools"):
                _set_active_view("documents")
                st.rerun()

    # D. Voice Assistant Card
    with low_col4:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">Voice Assistant</div>
                </div>
                <div class="soundwave-container">
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                </div>
                <div style="text-align: center; font-size: 0.78rem; font-weight: 600; color: #64748b; margin-bottom: 0.5rem;">
                    Listening...<br><span style="font-size: 0.72rem; color: #94a3b8; font-weight: 400;">Say a command or ask something</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🎙️ Speak Command", key="btn_speak_voice", type="primary", use_container_width=True):
            st.session_state["lucora_voice_listening"] = True
            st.session_state["aira_voice_listening"] = True
            st.toast("Transcribing voice command: 'Send email to Chetan about project update'", icon="🎙️")
            orchestrator.submit_instruction("Send an email to chetan@enterprise.com with project update.")
            st.rerun()

        st.caption("💡 *Try saying: \"Send email to Chetan about project update\"*")

    st.write("")

    # --------------------------------------------------------------------------
    # 4. Bottom 3-Card Row: Command Center Terminal | Journals | Bookmarks
    # --------------------------------------------------------------------------
    bot_col1, bot_col2, bot_col3 = st.columns([5, 3, 3])

    # A. Command Center Active Terminal
    with bot_col1:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">💻 Command Center</div>
                    <span class="aira-card-link lucora-card-link">View All Commands</span>
                </div>
                <div class="terminal-container">
                    <span class="terminal-prompt">></span> <span class="terminal-cmd">send email to chetan with project update</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-success">email sent successfully (Msg ID: 18f9e120bc7129ac)</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-cmd">summarize Q1_Report.pdf</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-success">summary created (4 key takeaways extracted)</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-cmd">schedule meeting with team tomorrow 11am</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-success">meeting scheduled (Meet ID: evt-a1b2c3)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # B. Journals Card
    with bot_col2:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">📖 Journals</div>
                    <span class="aira-card-link lucora-card-link">View All</span>
                </div>
                <div class="activity-item">
                    <div>
                        <div class="activity-title">21 May 2025</div>
                        <div class="activity-sub">Worked on project automation and email integration.</div>
                    </div>
                </div>
                <div class="activity-item">
                    <div>
                        <div class="activity-title">20 May 2025</div>
                        <div class="activity-sub">Researched file data extraction and AI tools.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # C. Bookmarks Card
    with bot_col3:
        st.markdown(
            """
            <div class="aira-card lucora-card">
                <div class="aira-card-header lucora-card-header">
                    <div class="aira-card-title lucora-card-title">🔖 Bookmarks</div>
                    <span class="aira-card-link lucora-card-link">View All</span>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #f5f3ff; color: #7c3aed;">🔗</div>
                    <div>
                        <div class="activity-title"><a href="https://platform.openai.com/docs" target="_blank" style="color: inherit; text-decoration: none;">OpenAI API Documentation</a></div>
                        <div class="activity-sub">https://platform.openai.com/docs</div>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #f5f3ff; color: #7c3aed;">🔗</div>
                    <div>
                        <div class="activity-title"><a href="https://developers.google.com/gmail/api" target="_blank" style="color: inherit; text-decoration: none;">Gmail API Quickstart</a></div>
                        <div class="activity-sub">https://developers.google.com/gmail/api</div>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon" style="background: #f5f3ff; color: #7c3aed;">🔗</div>
                    <div>
                        <div class="activity-title"><a href="https://docs.streamlit.io" target="_blank" style="color: inherit; text-decoration: none;">Streamlit Docs</a></div>
                        <div class="activity-sub">https://docs.streamlit.io</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Backward-compatibility alias
render_aira_dashboard = render_lucora_dashboard
