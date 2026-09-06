"""
ENMA Master Enterprise Dashboard Component.
Luxury Dark Wine / Crimson Glassmorphic Command Center with Ambient Wave Backdrop.
"""

from __future__ import annotations
import streamlit as st
import datetime

from agent.orchestrator import AgentOrchestrator, WorkflowState
from components.draft_card import render_draft_card
from components.clarification_modal import render_clarification_card
from components.timeline import render_timeline
from components.email_composer import render_email_composer, PREBUILT_TEMPLATES
from database.repository import ENMARepository, LUCORARepository, AIRARepository
from tools.calendar.calendar_tool import CalendarScheduleTool

def _set_active_view(view_name: str) -> None:
    st.session_state["enma_active_view"] = view_name
    st.session_state["lucora_active_view"] = view_name
    st.session_state["aira_active_view"] = view_name

def render_enma_dashboard(orchestrator: AgentOrchestrator, on_navigate_view) -> None:
    repo = ENMARepository()
    metrics = repo.get_task_metrics()

    # 1. Hero Greeting Banner Card (with cursive note & command bar)
    st.markdown(
        """
        <div class="enma-hero-banner">
            <div class="enma-hero-inner">
                <div class="enma-status-badge">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background: #10b981; box-shadow: 0 0 6px #10b981;"></span>
                    <span>ENMA is active</span>
                </div>
                <div class="enma-cursive-note">Less manual work, more you. ✦</div>
                <div class="enma-hero-headline">
                    <span style="color: #f43f5e;">✦</span> Hi Vaishnavi — Good to see you!
                </div>
                <div class="enma-hero-subtext">
                    Your AI assistant is ready to help you get things done. Ask, automate, create, or just say what you need.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Express Interactive Prompt Console
    with st.container():
        col_in, col_btn = st.columns([5.5, 1.2])
        with col_in:
            hero_task_input = st.text_input(
                "Command",
                placeholder='Ask anything or enter a command (e.g. "Send email to chetan@enterprise.com with project update")...',
                label_visibility="collapsed",
                key="enma_hero_prompt_input",
            )
        with col_btn:
            run_hero_prompt = st.button("Execute ✦", use_container_width=True, type="primary", key="enma_hero_run_btn")

        # Action Chips Row
        chip1, chip2, chip3, chip4, chip5 = st.columns(5)
        with chip1:
            if st.button("✉️ Draft Email", use_container_width=True, key="chip_email"):
                _set_active_view("tasks")
                st.session_state["main_composer_active_tab"] = "composer"
                st.rerun()
        with chip2:
            if st.button("📄 Summarize Doc", use_container_width=True, key="chip_doc"):
                _set_active_view("documents")
                st.rerun()
        with chip3:
            if st.button("📅 Schedule Meeting", use_container_width=True, key="chip_cal"):
                _set_active_view("calendar")
                st.rerun()
        with chip4:
            if st.button("📊 Analyze Data", use_container_width=True, key="chip_data"):
                _set_active_view("documents")
                st.rerun()
        with chip5:
            if st.button("⋮⋮ More Actions", use_container_width=True, key="chip_more"):
                _set_active_view("settings")
                st.rerun()

    if run_hero_prompt and hero_task_input:
        with st.spinner("ENMA AI synthesizing plan..."):
            orchestrator.submit_instruction(hero_task_input)
        _set_active_view("tasks")
        st.rerun()

    st.write("")

    # 2. Main Grid: Left/Center Productivity Core (68%) | Right Pulse (32%)
    main_col, side_col = st.columns([2.1, 1.0])

    with main_col:
        # 3-Column Mid Grid (Task Progress, Productivity Snapshot, AI Suggested Next)
        sub1, sub2, sub3 = st.columns(3)

        with sub1:
            st.markdown(
                """
                <div class="enma-dark-card" style="height: 100%;">
                    <div class="enma-card-header-row">
                        <span class="enma-card-title">⚡ AI Task Progress</span>
                        <span class="enma-status-tag enma-tag-gray">3/5</span>
                    </div>
                    <div class="enma-progress-bar-wrap">
                        <div class="enma-progress-bar-fill"></div>
                    </div>
                    <div class="enma-task-item">
                        <span><span class="enma-dot-green"></span>Processing 24 emails</span>
                    </div>
                    <div class="enma-task-item">
                        <span><span class="enma-dot-green"></span>Summarizing client report</span>
                    </div>
                    <div class="enma-task-item">
                        <span><span class="enma-dot-purple"></span>Updating tracker</span>
                        <span class="enma-status-tag enma-tag-purple">In progress</span>
                    </div>
                    <div class="enma-task-item">
                        <span><span class="enma-dot-gray"></span>Calendar sync</span>
                        <span class="enma-status-tag enma-tag-gray">Queued</span>
                    </div>
                    <div class="enma-task-item">
                        <span><span class="enma-dot-gray"></span>Doc analysis</span>
                        <span class="enma-status-tag enma-tag-gray">Queued</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sub2:
            st.markdown(
                f"""
                <div class="enma-dark-card" style="height: 100%;">
                    <div class="enma-card-header-row">
                        <span class="enma-card-title">📊 Productivity</span>
                        <span class="enma-card-link">This Week →</span>
                    </div>
                    <div class="enma-metrics-3grid">
                        <div class="enma-metric-mini-tile">
                            <div class="enma-metric-mini-icon">✉️</div>
                            <div class="enma-metric-mini-val">{metrics['emails_sent']}</div>
                            <div class="enma-metric-mini-label">Emails</div>
                            <div class="enma-metric-mini-delta">↑ 12%</div>
                        </div>
                        <div class="enma-metric-mini-tile">
                            <div class="enma-metric-mini-icon">📋</div>
                            <div class="enma-metric-mini-val">{metrics['completed']}</div>
                            <div class="enma-metric-mini-label">Tasks</div>
                            <div class="enma-metric-mini-delta">↑ 25%</div>
                        </div>
                        <div class="enma-metric-mini-tile">
                            <div class="enma-metric-mini-icon">👥</div>
                            <div class="enma-metric-mini-val">{metrics['events_today']}</div>
                            <div class="enma-metric-mini-label">Meets</div>
                            <div class="enma-metric-mini-delta">↑ 20%</div>
                        </div>
                    </div>
                    <div class="enma-quote-banner">
                        ✦ "Consistency builds momentum."
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sub3:
            st.markdown(
                """
                <div class="enma-dark-card" style="height: 100%;">
                    <div class="enma-card-header-row">
                        <span class="enma-card-title">✦ AI Suggested Next</span>
                        <span class="enma-status-tag enma-tag-purple">3</span>
                    </div>
                    <div class="enma-suggestion-tile">
                        <div class="enma-suggestion-text">📄 Summarize today's meeting notes from 11 AM</div>
                        <span style="color: #fda4af; font-size: 0.9rem;">›</span>
                    </div>
                    <div class="enma-suggestion-tile">
                        <div class="enma-suggestion-text">✉️ Follow up with client on pending proposal</div>
                        <span style="color: #fda4af; font-size: 0.9rem;">›</span>
                    </div>
                    <div class="enma-suggestion-tile">
                        <div class="enma-suggestion-text">📈 Prepare weekly progress report (last 7 days)</div>
                        <span style="color: #fda4af; font-size: 0.9rem;">›</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        # Row 2: Email Studio & Templates (Luxury Light Card)
        st.markdown(
            """
            <div class="enma-email-studio-card">
                <div class="enma-studio-top-header">
                    <div class="enma-studio-title">
                        <span>✉️</span> Email Studio & Templates
                    </div>
                </div>
                <div style="font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.8rem;">
                    POPULAR PREBUILT TEMPLATES
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 8 Template Buttons in 4x2 Grid
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        with t_col1:
            if st.button("📅 Meeting Request", help="Schedule a meeting", use_container_width=True, key="btn_tmpl_meet"):
                _set_template_and_navigate("Meeting Request")
            if st.button("🚀 Client Proposal", help="Business", use_container_width=True, key="btn_tmpl_prop"):
                _set_template_and_navigate("Client Proposal")
        with t_col2:
            if st.button("📄 Leave Application", help="HR & leave", use_container_width=True, key="btn_tmpl_leave"):
                _set_template_and_navigate("Leave Application")
            if st.button("⚠️ Urgent Alert", help="Important / Escalation", use_container_width=True, key="btn_tmpl_urg"):
                _set_template_and_navigate("Urgent Alert")
        with t_col3:
            if st.button("📊 Project Status", help="Update stakeholders", use_container_width=True, key="btn_tmpl_stat"):
                _set_template_and_navigate("Project Status")
            if st.button("📑 Document Review", help="Feedback / Review", use_container_width=True, key="btn_tmpl_docr"):
                _set_template_and_navigate("Document Review")
        with t_col4:
            if st.button("🎓 BTech Major Project", help="Academic / Project", use_container_width=True, key="btn_tmpl_btech"):
                _set_template_and_navigate("BTech Major Project")
            if st.button("👥 Weekly Sync Agenda", help="Team sync", use_container_width=True, key="btn_tmpl_synca"):
                _set_template_and_navigate("Weekly Sync Agenda")

        st.write("")
        render_email_composer(key_prefix="dash_")

    with side_col:
        # Card 1: Today's Schedule
        st.markdown(
            """
            <div class="enma-dark-card">
                <div class="enma-card-header-row">
                    <span class="enma-card-title">📅 Today's Schedule</span>
                    <span class="enma-card-link">View Calendar →</span>
                </div>
                <div style="font-size: 0.82rem; margin-bottom: 0.75rem; border-left: 2px solid #7c1a3b; padding-left: 0.8rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #fda4af; font-weight: 700; font-size: 0.76rem;">09:00 AM</span>
                        <span class="enma-status-tag enma-tag-green">Live</span>
                    </div>
                    <div style="font-weight: 700; color: #ffffff;">Daily Engineering Standup</div>
                    <div style="font-size: 0.72rem; color: #e2cad2;">30 mins • Team sync</div>
                </div>
                <div style="font-size: 0.82rem; margin-bottom: 0.75rem; border-left: 2px solid #7c1a3b; padding-left: 0.8rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #fda4af; font-weight: 700; font-size: 0.76rem;">11:00 AM</span>
                        <span class="enma-status-tag enma-tag-gray">Upcoming</span>
                    </div>
                    <div style="font-weight: 700; color: #ffffff;">Sprint Planning & Architecture</div>
                    <div style="font-size: 0.72rem; color: #e2cad2;">1 hour • Google Meet</div>
                </div>
                <div style="font-size: 0.82rem; margin-bottom: 0.75rem; border-left: 2px solid #7c1a3b; padding-left: 0.8rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #fda4af; font-weight: 700; font-size: 0.76rem;">02:00 PM</span>
                        <span class="enma-status-tag enma-tag-gray">Upcoming</span>
                    </div>
                    <div style="font-weight: 700; color: #ffffff;">Client Demonstration</div>
                    <div style="font-size: 0.72rem; color: #e2cad2;">1 hour • Live feature walk</div>
                </div>
                <div style="font-size: 0.82rem; border-left: 2px solid #7c1a3b; padding-left: 0.8rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #fda4af; font-weight: 700; font-size: 0.76rem;">04:30 PM</span>
                        <span class="enma-status-tag enma-tag-gray">Upcoming</span>
                    </div>
                    <div style="font-weight: 700; color: #ffffff;">Review & Deliverables Wrap-up</div>
                    <div style="font-size: 0.72rem; color: #e2cad2;">30 mins • Summary</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 2: Recent Activity Stream
        st.markdown(
            """
            <div class="enma-dark-card">
                <div class="enma-card-header-row">
                    <span class="enma-card-title">🕒 Recent Activity</span>
                    <span class="enma-card-link">View All →</span>
                </div>
                <div class="enma-task-item" style="flex-direction: column; align-items: flex-start; gap: 2px;">
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <span style="font-weight: 700; color: #ffffff;"><span class="enma-dot-green"></span>Email dispatched to Chetan</span>
                        <span style="color: #fda4af; font-size: 0.7rem;">10:30 AM</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 13px;">Project update and next steps</div>
                </div>
                <div class="enma-task-item" style="flex-direction: column; align-items: flex-start; gap: 2px;">
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <span style="font-weight: 700; color: #ffffff;"><span class="enma-dot-purple"></span>Document summary synthesized</span>
                        <span style="color: #fda4af; font-size: 0.7rem;">09:15 AM</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 13px;">Q1_Report.pdf (4 takeaways)</div>
                </div>
                <div class="enma-task-item" style="flex-direction: column; align-items: flex-start; gap: 2px;">
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <span style="font-weight: 700; color: #ffffff;"><span class="enma-dot-green"></span>Meeting scheduled</span>
                        <span style="color: #fda4af; font-size: 0.7rem;">09:00 AM</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 13px;">Team sync on 24 May, 11:00 AM</div>
                </div>
                <div class="enma-task-item" style="flex-direction: column; align-items: flex-start; gap: 2px;">
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <span style="font-weight: 700; color: #ffffff;"><span class="enma-dot-gray"></span>Data extracted from sales.xlsx</span>
                        <span style="color: #fda4af; font-size: 0.7rem;">Yesterday</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 13px;">5 tables & 2 charts generated</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 3: Voice Command Engine
        st.markdown(
            """
            <div class="enma-voice-card">
                <div class="enma-voice-inner">
                    <div class="enma-card-header-row">
                        <span class="enma-card-title">🎙️ Voice Command Engine</span>
                        <span class="enma-status-tag enma-tag-green">Listening</span>
                    </div>
                    <div class="enma-soundwave-wrap">
                        <div class="enma-wave-bar"></div>
                        <div class="enma-wave-bar"></div>
                        <div class="enma-wave-bar"></div>
                        <div class="enma-wave-bar"></div>
                        <div class="enma-wave-bar"></div>
                        <div class="enma-wave-bar"></div>
                        <div class="enma-wave-bar"></div>
                        <div class="enma-wave-bar"></div>
                    </div>
                    <div style="font-size: 0.78rem; color: #fecdd3; margin-bottom: 0.8rem;">
                        Tap to speak or say <strong>"Hey ENMA"</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🎙️ Speak Command Now", key="btn_dash_mic_trigger", type="primary", use_container_width=True):
            st.toast("Transcribed: 'Schedule sprint planning meeting tomorrow at 11 AM'", icon="🎙")
            _set_active_view("calendar")
            st.rerun()

        # Card 4: Workspace Health Footer
        st.markdown(
            """
            <div class="enma-dark-card" style="padding: 0.9rem 1.1rem; display: flex; align-items: center; justify-content: space-between; margin-top: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 1.2rem;">🌱</span>
                    <div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #ffffff;">Your workspace is running smoothly</div>
                        <div style="font-size: 0.7rem; color: #a7f3d0;">All systems operational • 99.9% uptime</div>
                    </div>
                </div>
                <span style="color: #fda4af; font-size: 1rem;">›</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

def _set_template_and_navigate(tmpl_name: str):
    if tmpl_name in PREBUILT_TEMPLATES:
        t = PREBUILT_TEMPLATES[tmpl_name]
        st.session_state["dash_composer_subject"] = t["subject"]
        st.session_state["dash_composer_body"] = t["body"]
        st.session_state["main_composer_subject"] = t["subject"]
        st.session_state["main_composer_body"] = t["body"]
        st.toast(f"Loaded '{tmpl_name}' template", icon="✓")

# Backward compatibility aliases
render_lucora_dashboard = render_enma_dashboard
render_aira_dashboard = render_enma_dashboard
