"""
ENMA Master Dashboard Component.
Bright, Clean & Light Formal Corporate Palette.
"""

from __future__ import annotations
import streamlit as st

from agent.orchestrator import AgentOrchestrator
from database.repository import ENMARepository
from components.email_composer import render_email_composer, PREBUILT_TEMPLATES

def _set_active_view(view_name: str):
    st.session_state["enma_active_view"] = view_name
    st.session_state["lucora_active_view"] = view_name
    st.session_state["aira_active_view"] = view_name

def render_enma_dashboard(orchestrator: AgentOrchestrator, on_navigate_view) -> None:
    """Renders the bright, light formal ENMA executive dashboard."""
    repo = ENMARepository()
    metrics = repo.get_task_metrics()

    # 1. Hero Greeting & Command Banner (Light Formal Theme with .hero-wave & cursive note)
    st.markdown(
        """
        <div style="position: relative; border-radius: 16px; background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 60%, #e0e7ff 100%); border: 1px solid #bfdbfe; padding: 24px; overflow: hidden; box-shadow: 0 4px 20px rgba(37, 99, 235, 0.08); margin-bottom: 20px;">
            <div class="hero-wave"></div>
            <div style="position: absolute; right: 32px; top: 20px; user-select: none; pointer-events: none;">
                <p style="font-family: 'Caveat', cursive; font-size: 24px; color: #1d4ed8; transform: rotate(-3deg); letter-spacing: 0.02em; margin: 0;">
                    Less manual work, more you. <span style="color: #2563eb;">✦</span>
                </p>
            </div>
            <div style="position: relative; z-index: 10;">
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 9999px; background: #ffffff; border: 1px solid #cbd5e1; font-size: 11px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #059669; box-shadow: 0 0 6px #059669;"></span>
                    <span style="color: #0f172a; font-weight: 600; letter-spacing: 0.02em;">ENMA is active</span>
                </div>
                <div style="margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: #2563eb; font-size: 20px;">✦</span>
                        <h2 style="font-size: 24px; font-weight: 800; letter-spacing: -0.01em; color: #0f172a; margin: 0;">Hi Hriday — Good to see you!</h2>
                    </div>
                    <p style="font-size: 13px; color: #475569; max-width: 650px; line-height: 1.5; margin: 4px 0 0 0;">
                        Your AI assistant is ready to help you get things done. Ask, automate, create, or just say what you need.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Interactive Central Input Bar
    with st.container():
        col_in, col_btn = st.columns([5.5, 1.2])
        with col_in:
            hero_task_input = st.text_input(
                "Command",
                placeholder='Ask anything or enter a command (e.g. "Send email to chetan@enterprise.com with project update")...',
                label_visibility="collapsed",
                key="enma_hero_prompt_input_exact",
            )
        with col_btn:
            run_hero_prompt = st.button("Execute ✦", use_container_width=True, type="primary", key="enma_hero_run_btn_exact")

        # Quick Action Buttons Row (Aesthetic Symbols Only)
        q1, q2, q3, q4, q5 = st.columns(5)
        with q1:
            if st.button("◇ Draft Email", use_container_width=True, key="btn_quick_draft_mail"):
                _set_active_view("tasks")
                st.session_state["dash_composer_active_tab"] = "composer"
                st.rerun()
        with q2:
            if st.button("⬡ Summarize Doc", use_container_width=True, key="btn_quick_sum_doc"):
                _set_active_view("documents")
                st.rerun()
        with q3:
            if st.button("◈ Schedule Meeting", use_container_width=True, key="btn_quick_sched_meet"):
                _set_active_view("calendar")
                st.rerun()
        with q4:
            if st.button("◲ Analyze Data", use_container_width=True, key="btn_quick_ana_data"):
                _set_active_view("documents")
                st.rerun()
        with q5:
            if st.button("⎈ More Actions", use_container_width=True, key="btn_quick_more_act"):
                _set_active_view("settings")
                st.rerun()

    if run_hero_prompt and hero_task_input:
        with st.spinner("ENMA AI synthesizing plan..."):
            orchestrator.submit_instruction(hero_task_input)
        _set_active_view("tasks")
        st.rerun()

    st.write("")

    # 2. Main 12-Column Grid: Left (8 Cols) | Right (4 Cols)
    main_col, side_col = st.columns([2.1, 1.0])

    with main_col:
        # 3 Cards in a Row: Task Progress, Productivity Snapshot, AI Suggested Next
        sub1, sub2, sub3 = st.columns(3)

        with sub1:
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; height: 100%; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 8px;">
                        <span style="display: flex; align-items: center; gap: 6px; color: #2563eb;">
                            <svg style="width: 14px; height: 14px; fill: currentColor;" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                            <span style="color: #0f172a;">AI Task Progress</span>
                        </span>
                        <span style="color: #64748b; font-size: 12px;">&gt;</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: #64748b; margin-bottom: 6px;">
                        <span style="display: flex; align-items: center; gap: 4px;">
                            <span style="width: 6px; height: 6px; border-radius: 50%; background: #2563eb;"></span> Active Automations
                        </span>
                        <span style="font-weight: 700; color: #0f172a;">3/5</span>
                    </div>
                    <div style="width: 100%; height: 6px; background: #e2e8f0; border-radius: 9999px; overflow: hidden; margin-bottom: 12px;">
                        <div style="height: 100%; width: 60%; background: linear-gradient(90deg, #1d4ed8 0%, #3b82f6 100%); border-radius: 9999px;"></div>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 11px;">
                        <div style="display: flex; align-items: center; gap: 8px; color: #059669;">
                            <span>✓</span>
                            <span style="color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Processing 24 emails</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; color: #059669;">
                            <span>✓</span>
                            <span style="color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Summarizing client report</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; color: #334155;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="width: 7px; height: 7px; border-radius: 50%; background: #2563eb;"></span> Updating tracker
                            </span>
                            <span style="font-size: 9px; color: #1d4ed8; background: #eff6ff; border: 1px solid #bfdbfe; padding: 2px 6px; border-radius: 4px; font-weight: 600;">In progress</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; color: #64748b;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="width: 7px; height: 7px; border-radius: 50%; background: #cbd5e1;"></span> Calendar sync
                            </span>
                            <span style="font-size: 9px; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 2px 6px; border-radius: 4px;">Queued</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; color: #64748b;">
                            <span style="width: 7px; height: 7px; border-radius: 50%; background: #cbd5e1;"></span> Document analysis
                            <span style="font-size: 9px; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 2px 6px; border-radius: 4px;">Queued</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sub2:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; height: 100%; box-shadow: 0 1px 3px rgba(15,23,42,0.04); display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 12px;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="color: #2563eb;">◈</span>
                                <span>Productivity Snapshot</span>
                            </span>
                            <span style="font-size: 10px; color: #64748b; cursor: pointer;">This Week ▼</span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-bottom: 12px;">
                            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 4px;">
                                <span style="color: #2563eb; font-size: 12px; margin-bottom: 2px; display: block;">◇</span>
                                <span style="font-size: 14px; font-weight: 800; color: #0f172a; display: block;">{metrics['emails_sent']}</span>
                                <span style="font-size: 9px; color: #64748b; display: block;">Emails Sent</span>
                                <span style="font-size: 8px; color: #059669; font-weight: 700;">↑ 12%</span>
                            </div>
                            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 4px;">
                                <span style="color: #2563eb; font-size: 12px; margin-bottom: 2px; display: block;">✓</span>
                                <span style="font-size: 14px; font-weight: 800; color: #0f172a; display: block;">{metrics['completed']}</span>
                                <span style="font-size: 9px; color: #64748b; display: block;">Tasks Done</span>
                                <span style="font-size: 8px; color: #059669; font-weight: 700;">↑ 25%</span>
                            </div>
                            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 4px;">
                                <span style="color: #2563eb; font-size: 12px; margin-bottom: 2px; display: block;">◈</span>
                                <span style="font-size: 14px; font-weight: 800; color: #0f172a; display: block;">{metrics['events_today']}</span>
                                <span style="font-size: 9px; color: #64748b; display: block;">Meetings</span>
                                <span style="font-size: 8px; color: #059669; font-weight: 700;">↑ 20%</span>
                            </div>
                        </div>
                    </div>
                    <div style="background: #eff6ff; border-radius: 10px; padding: 8px; text-align: center; border: 1px solid #bfdbfe;">
                        <p style="font-size: 10px; color: #1e40af; font-style: italic; margin: 0;">
                            <span style="color: #2563eb; font-style: normal;">✦</span> "Consistency builds momentum."
                        </p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sub3:
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; height: 100%; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 12px;">
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <span style="color: #2563eb;">✦</span>
                            <span>AI Suggested Next</span>
                        </span>
                        <span style="width: 18px; height: 18px; border-radius: 50%; background: #eff6ff; border: 1px solid #bfdbfe; font-size: 10px; display: flex; align-items: center; justify-content: center; color: #1d4ed8; font-weight: 700;">3</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="padding: 8px 10px; border-radius: 10px; background: #f8fafc; border: 1px solid #e2e8f0; cursor: pointer;">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 12px; color: #2563eb;">◲</span>
                                    <p style="font-size: 11px; color: #0f172a; font-weight: 600; margin: 0;">Summarize today's meeting notes</p>
                                </div>
                                <span style="font-size: 10px; color: #64748b;">&gt;</span>
                            </div>
                            <span style="font-size: 9px; color: #64748b; margin-left: 20px; display: block;">from 11 AM</span>
                        </div>
                        <div style="padding: 8px 10px; border-radius: 10px; background: #f8fafc; border: 1px solid #e2e8f0; cursor: pointer;">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 12px; color: #2563eb;">◇</span>
                                    <p style="font-size: 11px; color: #0f172a; font-weight: 600; margin: 0;">Follow up with client on proposal</p>
                                </div>
                                <span style="font-size: 10px; color: #64748b;">&gt;</span>
                            </div>
                            <span style="font-size: 9px; color: #64748b; margin-left: 20px; display: block;">pending proposal</span>
                        </div>
                        <div style="padding: 8px 10px; border-radius: 10px; background: #f8fafc; border: 1px solid #e2e8f0; cursor: pointer;">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 12px; color: #2563eb;">◈</span>
                                    <p style="font-size: 11px; color: #0f172a; font-weight: 600; margin: 0;">Prepare weekly progress report</p>
                                </div>
                                <span style="font-size: 10px; color: #64748b;">&gt;</span>
                            </div>
                            <span style="font-size: 9px; color: #64748b; margin-left: 20px; display: block;">(using last 7 days data)</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        # Row 2: Bottom Email Studio & Templates (Inside Left 8 cols)
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 1px 3px rgba(15,23,42,0.04); margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #2563eb; font-size: 16px;">◇</span>
                        <h3 style="font-size: 14px; font-weight: 700; color: #0f172a; margin: 0;">Email Studio &amp; Templates</h3>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 16px; font-size: 12px; font-weight: 500; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 14px;">
                    <span style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 6px; font-weight: 700;">Templates</span>
                    <span style="color: #64748b; cursor: pointer;">Automation Toolkits</span>
                    <span style="color: #64748b; cursor: pointer;">Command Center Logs</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Popular Templates</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 8 Template Buttons in 4x2 Grid (Aesthetic Symbols)
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        with t_col1:
            if st.button("◈ Meeting Request", help="Schedule a meeting", use_container_width=True, key="btn_tmpl_meet_ex"):
                _set_template_and_navigate("Meeting Request")
            if st.button("◇ Client Proposal", help="Business proposal", use_container_width=True, key="btn_tmpl_prop_ex"):
                _set_template_and_navigate("Client Proposal")
        with t_col2:
            if st.button("⬡ Leave Application", help="HR & leave request", use_container_width=True, key="btn_tmpl_leave_ex"):
                _set_template_and_navigate("Leave Application")
            if st.button("◬ Urgent Alert", help="Important / Escalation", use_container_width=True, key="btn_tmpl_urg_ex"):
                _set_template_and_navigate("Urgent Alert")
        with t_col3:
            if st.button("◲ Project Status", help="Update stakeholders", use_container_width=True, key="btn_tmpl_stat_ex"):
                _set_template_and_navigate("Project Status")
            if st.button("◫ Document Review", help="Feedback & review", use_container_width=True, key="btn_tmpl_docr_ex"):
                _set_template_and_navigate("Document Review")
        with t_col4:
            if st.button("✦ BTech Major Project", help="Academic progress report", use_container_width=True, key="btn_tmpl_btech_ex"):
                _set_template_and_navigate("BTech Major Project")
            if st.button("⎈ Weekly Sync Agenda", help="Team engineering sync", use_container_width=True, key="btn_tmpl_synca_ex"):
                _set_template_and_navigate("Weekly Sync Agenda")

        st.write("")
        # Call email composer without duplicating template selector buttons
        render_email_composer(key_prefix="dash_exact_", show_templates_picker=False)

    with side_col:
        # Right Column (4 Cols): Today's Schedule, Recent Activity, Voice Engine, System Health
        # Card 1: Today's Schedule
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.04); margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 12px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <span style="color: #2563eb;">◈</span>
                        <span>Today's Schedule</span>
                    </span>
                    <span style="font-size: 10px; color: #2563eb; cursor: pointer; font-weight: 600;">View Calendar →</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 12px; position: relative;">
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 3px solid #2563eb; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #64748b; display: block;">09:00 AM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Daily Engineering Standup</p>
                            <p style="font-size: 10px; color: #64748b; margin: 0;">30 mins · Team sync</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; border-radius: 9999px;">Live</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 3px solid #cbd5e1; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #64748b; display: block;">11:00 AM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Sprint Planning &amp; Architecture</p>
                            <p style="font-size: 10px; color: #64748b; margin: 0;">1 hour · Google Meet</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; border-radius: 9999px;">Upcoming</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 3px solid #cbd5e1; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #64748b; display: block;">02:00 PM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Client Demonstration</p>
                            <p style="font-size: 10px; color: #64748b; margin: 0;">1 hour · Live feature walk</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; border-radius: 9999px;">Upcoming</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 3px solid #cbd5e1; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #64748b; display: block;">04:30 PM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Review &amp; Deliverables Wrap-up</p>
                            <p style="font-size: 10px; color: #64748b; margin: 0;">30 mins · Summary</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; border-radius: 9999px;">Upcoming</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 2: Recent Activity
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.04); margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 12px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <span style="color: #2563eb;">◈</span>
                        <span>Recent Activity</span>
                    </span>
                    <span style="font-size: 10px; color: #2563eb; cursor: pointer; font-weight: 600;">View All →</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 11px;">
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #059669; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Email dispatched to Chetan</p>
                                <p style="font-size: 10px; color: #64748b; margin: 0;">Project update and next steps</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #94a3b8;">10:30 AM</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #2563eb; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Document summary synthesized</p>
                                <p style="font-size: 10px; color: #64748b; margin: 0;">Q1_Report.pdf (4 takeaways)</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #94a3b8;">09:15 AM</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #d97706; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Meeting scheduled</p>
                                <p style="font-size: 10px; color: #64748b; margin: 0;">Team sync on 24 May, 11:00 AM</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #94a3b8;">09:00 AM</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #4f46e5; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #0f172a; line-height: 1.2; margin: 0;">Data extracted from sales.xlsx</p>
                                <p style="font-size: 10px; color: #64748b; margin: 0;">5 tables &amp; 2 charts generated</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #94a3b8;">Yesterday</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 3: Voice Command Engine
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.04); text-align: center; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 8px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <svg style="width: 16px; height: 16px; color: #2563eb;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"></path></svg>
                        <span>Voice Command Engine</span>
                    </span>
                    <span style="padding: 2px 8px; border-radius: 9999px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 9px; font-weight: 600;">
                        ● Listening
                    </span>
                </div>
                <div style="height: 40px; display: flex; align-items: center; justify-content: center; gap: 6px; margin: 8px 0;">
                    <span class="wave-bar" style="width: 4px; background: #2563eb; border-radius: 9999px; height: 12px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #1d4ed8; border-radius: 9999px; height: 22px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #3b82f6; border-radius: 9999px; height: 18px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #2563eb; border-radius: 9999px; height: 28px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #1d4ed8; border-radius: 9999px; height: 14px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #3b82f6; border-radius: 9999px; height: 26px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #2563eb; border-radius: 9999px; height: 20px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #1d4ed8; border-radius: 9999px; height: 16px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #3b82f6; border-radius: 9999px; height: 24px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #2563eb; border-radius: 9999px; height: 10px;"></span>
                </div>
                <p style="font-size: 11px; color: #64748b; margin-bottom: 12px;">Tap to speak or say "Hey ENMA"</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⍾ Speak Command Now", key="btn_dash_mic_trigger_exact", type="primary", use_container_width=True):
            st.toast("Transcribed: 'Schedule sprint planning meeting tomorrow at 11 AM'")
            _set_active_view("calendar")
            st.rerun()

        # Card 4: System Status / Workspace Health
        st.markdown(
            """
            <div style="position: relative; background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%); border: 1px solid #bbf7d0; border-radius: 14px; padding: 14px; display: flex; align-items: center; justify-content: space-between; overflow: hidden; box-shadow: 0 1px 3px rgba(15,23,42,0.04); margin-top: 8px;">
                <div class="footer-wave"></div>
                <div style="display: flex; align-items: center; gap: 10px; position: relative; z-index: 10;">
                    <span style="font-size: 16px; color: #059669;">✦</span>
                    <div style="line-height: 1.1;">
                        <p style="font-size: 12px; font-weight: 700; color: #0f172a; margin: 0;">Workspace is running smoothly</p>
                        <p style="font-size: 10px; color: #059669; font-weight: 600; margin: 0;">All systems operational · 99.9% uptime</p>
                    </div>
                </div>
                <span style="color: #64748b; font-size: 12px; position: z-index: 10;">&gt;</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

def _set_template_and_navigate(tmpl_name: str):
    if tmpl_name in PREBUILT_TEMPLATES:
        t = PREBUILT_TEMPLATES[tmpl_name]
        st.session_state["dash_exact_email_subject"] = t["subject"]
        st.session_state["dash_exact_email_body"] = t["body"]
        st.session_state["dash_exact_composer_subject"] = t["subject"]
        st.session_state["dash_exact_composer_body"] = t["body"]
        st.session_state["main_email_subject"] = t["subject"]
        st.session_state["main_email_body"] = t["body"]
        st.session_state["main_composer_subject"] = t["subject"]
        st.session_state["main_composer_body"] = t["body"]
        st.toast(f"Loaded '{tmpl_name}' template")

# Backward compatibility aliases
render_lucora_dashboard = render_enma_dashboard
render_aira_dashboard = render_enma_dashboard
