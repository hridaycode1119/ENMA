"""
LUCORA Master Enterprise Dashboard Component.
Ultra-clean, creative, and aesthetic command center.
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
    """Renders the creative, aesthetic, and uncluttered LUCORA AI Dashboard."""
    
    repo = LUCORARepository()
    metrics = repo.get_task_metrics()

    # --------------------------------------------------------------------------
    # 1. Executive Metrics Ribbon (4 Cards)
    # --------------------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-accent-bar" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);"></div>
                <div class="kpi-top-row">
                    <span class="kpi-label">Tasks Automated</span>
                    <span class="kpi-badge badge-purple">↑ 18%</span>
                </div>
                <div class="kpi-val">{metrics['completed']}</div>
                <div class="kpi-delta">Processed successfully</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi2:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-accent-bar" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);"></div>
                <div class="kpi-top-row">
                    <span class="kpi-label">Emails Delivered</span>
                    <span class="kpi-badge badge-green">100% live</span>
                </div>
                <div class="kpi-val">{metrics['emails_sent']}</div>
                <div class="kpi-delta">Dispatched via Resend & Gmail</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi3:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-accent-bar" style="background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);"></div>
                <div class="kpi-top-row">
                    <span class="kpi-label">Files Processed</span>
                    <span class="kpi-badge badge-blue">Multi-Format</span>
                </div>
                <div class="kpi-val">{metrics['files_processed']}</div>
                <div class="kpi-delta">PDF, Word, Excel, CSV</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi4:
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-accent-bar" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);"></div>
                <div class="kpi-top-row">
                    <span class="kpi-label">Time Saved</span>
                    <span class="kpi-badge badge-orange">This week</span>
                </div>
                <div class="kpi-val">{metrics['time_saved_hours']}h</div>
                <div class="kpi-delta">Cumulative engineering hours</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --------------------------------------------------------------------------
    # 2. Main 2-Column Workspace: Intelligence Hub (Left) | Pulse Stream (Right)
    # --------------------------------------------------------------------------
    col_main, col_stream = st.columns([7, 4])

    with col_main:
        # A. Cognitive AI Command Studio
        st.markdown(
            """
            <div class="hero-prompt-card">
                <div class="hero-welcome-badge">✦ Cognitive Engine Active</div>
                <div class="hero-welcome-text">Hi Vaishnavi — Welcome to LUCORA</div>
                <div class="hero-welcome-sub">Type a natural-language command to execute actions across Gmail, Resend, Calendar, and Documents with safety verification.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick action chips
        chip_c1, chip_c2, chip_c3, chip_c4 = st.columns(4)
        with chip_c1:
            if st.button("Draft Status Email", key="chip_email_status", use_container_width=True):
                orchestrator.submit_instruction("Send an email to chetan@enterprise.com with project status update.")
                st.rerun()
        with chip_c2:
            if st.button("Summarize Document", key="chip_doc_sum", use_container_width=True):
                _set_active_view("documents")
                st.rerun()
        with chip_c3:
            if st.button("Schedule Meeting", key="chip_meet_sync", use_container_width=True):
                _set_active_view("calendar")
                st.rerun()
        with chip_c4:
            if st.button("Analyze Data File", key="chip_data_ext", use_container_width=True):
                _set_active_view("documents")
                st.rerun()

        # Conversational Task Prompt Box
        with st.form(key="lucora_hero_prompt_form"):
            user_prompt = st.text_input(
                "Command Prompt",
                placeholder="Ask anything or enter a command (e.g. 'Send email to chetan@enterprise.com with project update')...",
                label_visibility="collapsed",
            )
            submit_prompt = st.form_submit_button("Send Command →", type="primary", use_container_width=True)

            if submit_prompt and user_prompt.strip():
                with st.spinner("LUCORA reasoning over instruction..."):
                    orchestrator.submit_instruction(user_prompt.strip())
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

        st.write("")

        # B. Studio Workspaces (Tabs)
        tab_email, tab_tools, tab_terminal = st.tabs([
            "Email Studio & Templates",
            "Automation Toolkits",
            "Command Center Logs",
        ])

        with tab_email:
            render_email_composer(key_prefix="dash_")

        with tab_tools:
            st.caption("Quickly launch specialized cognitive tools:")
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                with st.container(border=True):
                    st.markdown("**Document Processing & AI Editor**")
                    st.caption("Inspect, polish, summarize, and convert PDF, DOCX, and Text documents.")
                    if st.button("Open Document Studio →", key="dash_tool_doc", use_container_width=True):
                        _set_active_view("documents")
                        st.rerun()

                with st.container(border=True):
                    st.markdown("**Data Extractor & Spreadsheet AI**")
                    st.caption("Extract structured tables, summary metrics, and insights from CSV / XLSX.")
                    if st.button("Launch Data Tools →", key="dash_tool_data", use_container_width=True):
                        _set_active_view("documents")
                        st.rerun()

            with t_col2:
                with st.container(border=True):
                    st.markdown("**Calendar & Meeting Scheduler**")
                    st.caption("Automate calendar events and Google Meet conference links.")
                    if st.button("Open Calendar →", key="dash_tool_cal", use_container_width=True):
                        _set_active_view("calendar")
                        st.rerun()

                with st.container(border=True):
                    st.markdown("**Notes & Knowledge Scratchpad**")
                    st.caption("Persist engineering logs and research notes with Supabase cloud sync.")
                    if st.button("Open Notes →", key="dash_tool_notes", use_container_width=True):
                        _set_active_view("notes")
                        st.rerun()

        with tab_terminal:
            st.markdown(
                """
                <div class="terminal-container">
                    <span class="terminal-prompt">></span> <span class="terminal-cmd">LUCORA v2.4 initialized on Linux</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-success">Loaded Gemini 1.5 Flash Cognitive Core</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-cmd">ToolRegistry: 6 dynamic tools registered</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-success">OAuth 2.0 PKCE & Resend API ready</span><br>
                    <span class="terminal-prompt">></span> <span class="terminal-cmd">Supabase cloud persistence active</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Right Column: Today's Schedule, Activity Stream & Voice
    with col_stream:
        # A. Today's Schedule Card
        st.markdown(
            """
            <div class="lucora-card">
                <div class="lucora-card-header">
                    <div class="lucora-card-title">Today's Schedule</div>
                    <span class="lucora-card-link">View Calendar</span>
                </div>
                <div class="timeline-item-clean">
                    <div class="timeline-time-badge">09:00 AM</div>
                    <div>
                        <div class="timeline-title">Daily Engineering Standup</div>
                        <div class="timeline-sub">30 mins • Team sync</div>
                    </div>
                </div>
                <div class="timeline-item-clean">
                    <div class="timeline-time-badge">11:00 AM</div>
                    <div>
                        <div class="timeline-title">Sprint Planning & Architecture Sync</div>
                        <div class="timeline-sub">1 hour • Google Meet</div>
                    </div>
                </div>
                <div class="timeline-item-clean">
                    <div class="timeline-time-badge">02:00 PM</div>
                    <div>
                        <div class="timeline-title">Client Demonstration</div>
                        <div class="timeline-sub">1 hour • Live feature walk</div>
                    </div>
                </div>
                <div class="timeline-item-clean">
                    <div class="timeline-time-badge">04:30 PM</div>
                    <div>
                        <div class="timeline-title">Review & Deliverables Wrap-up</div>
                        <div class="timeline-sub">30 mins • Summary</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        # B. Recent Autonomous Actions
        st.markdown(
            """
            <div class="lucora-card">
                <div class="lucora-card-header">
                    <div class="lucora-card-title">Recent Activity</div>
                    <span class="lucora-card-link">Audit Logs</span>
                </div>
                <div class="activity-row-clean">
                    <div class="activity-main">
                        <div class="activity-bullet" style="background: #10b981;"></div>
                        <div>
                            <div class="activity-name">Email dispatched to Chetan</div>
                            <div class="activity-detail">Project update and next steps</div>
                        </div>
                    </div>
                    <div class="activity-timestamp">10:30 AM</div>
                </div>
                <div class="activity-row-clean">
                    <div class="activity-main">
                        <div class="activity-bullet" style="background: #3b82f6;"></div>
                        <div>
                            <div class="activity-name">Document summary synthesized</div>
                            <div class="activity-detail">Q1_Report.pdf (4 takeaways)</div>
                        </div>
                    </div>
                    <div class="activity-timestamp">09:15 AM</div>
                </div>
                <div class="activity-row-clean">
                    <div class="activity-main">
                        <div class="activity-bullet" style="background: #f59e0b;"></div>
                        <div>
                            <div class="activity-name">Meeting scheduled</div>
                            <div class="activity-detail">Team sync on 24 May, 11:00 AM</div>
                        </div>
                    </div>
                    <div class="activity-timestamp">09:00 AM</div>
                </div>
                <div class="activity-row-clean">
                    <div class="activity-main">
                        <div class="activity-bullet" style="background: #8b5cf6;"></div>
                        <div>
                            <div class="activity-name">Data extracted from sales.xlsx</div>
                            <div class="activity-detail">5 tables & 2 charts generated</div>
                        </div>
                    </div>
                    <div class="activity-timestamp">Yesterday</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        # C. Minimal Voice Assistant Capsule
        st.markdown(
            """
            <div class="voice-wave-capsule">
                <div style="font-size: 0.82rem; font-weight: 700; color: #4f46e5; margin-bottom: 0.2rem;">Voice Command Engine</div>
                <div class="soundwave-container">
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                </div>
                <div style="font-size: 0.74rem; color: #64748b;">Ready to transcribe speech input</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🎙 Speak Natural Command", key="btn_dash_speak", type="primary", use_container_width=True):
            st.session_state["lucora_voice_listening"] = True
            st.toast("Transcribing voice command...", icon="🎙")
            orchestrator.submit_instruction("Send an email to chetan@enterprise.com with project update.")
            st.rerun()

# Backward-compatibility alias
render_aira_dashboard = render_lucora_dashboard
