"""
ENMA Master Enterprise Dashboard Component.
Exact Wine/Plum/Ruby Glassmorphic Palette & Layout from designe/code.html.
"""

from __future__ import annotations
import streamlit as st

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
    """Renders the exact ENMA dashboard from designe/code.html."""
    repo = ENMARepository()
    metrics = repo.get_task_metrics()

    # 1. Hero Greeting & Command Banner (with .hero-wave & cursive note)
    st.markdown(
        """
        <div style="position: relative; border-radius: 16px; background: linear-gradient(135deg, #230c18 0%, #2c0e1e 50%, #2b101f 100%); border: 1px solid rgba(244, 63, 118, 0.25); padding: 24px; overflow: hidden; box-shadow: 0 10px 30px rgba(20, 6, 13, 0.4); margin-bottom: 20px;">
            <div class="hero-wave"></div>
            <div style="position: absolute; right: 32px; top: 20px; user-select: none; pointer-events: none;">
                <p style="font-family: 'Caveat', cursive; font-size: 24px; color: rgba(252, 231, 243, 0.9); transform: rotate(-3deg); letter-spacing: 0.02em; filter: drop-shadow(0 2px 10px rgba(244,63,118,0.5)); margin: 0;">
                    Less manual work, more you. <span style="color: #ff4d8d;">✦</span>
                </p>
            </div>
            <div style="position: relative; z-index: 10;">
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 9999px; background: rgba(20, 6, 13, 0.7); border: 1px solid rgba(63, 23, 46, 0.6); font-size: 11px; margin-bottom: 12px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #34d399; box-shadow: 0 0 6px #34d399;"></span>
                    <span style="color: #ffffff; font-weight: 500; letter-spacing: 0.03em;">ENMA is active</span>
                </div                <div style="margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: #fb719e; font-size: 20px;">✦</span>
                        <h2 style="font-size: 24px; font-weight: 700; letter-spacing: -0.01em; color: #ffffff; margin: 0;">Hi Hriday — Good to see you!</h2>
                    </div>
                    <p style="font-size: 12px; color: rgba(252, 231, 243, 0.8); max-width: 650px; line-height: 1.5; margin: 4px 0 0 0;">
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
                <div style="background: rgba(35, 12, 24, 0.7); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 16px; height: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">
                        <span style="display: flex; align-items: center; gap: 6px; color: #fb719e;">
                            <svg style="width: 14px; height: 14px; fill: currentColor;" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                            <span style="color: #ffffff;">AI Task Progress</span>
                        </span>
                        <span style="color: #a88094; font-size: 12px;">&gt;</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: #a88094; margin-bottom: 6px;">
                        <span style="display: flex; align-items: center; gap: 4px;">
                            <span style="width: 6px; height: 6px; border-radius: 50%; background: #fb719e;"></span> Active Automations
                        </span>
                        <span style="font-weight: 600; color: #ffffff;">3/5</span>
                    </div>
                    <div style="width: 100%; height: 6px; background: #14060d; border-radius: 9999px; overflow: hidden; margin-bottom: 12px;">
                        <div style="height: 100%; width: 60%; background: linear-gradient(90deg, #f43f76 0%, #ff4d8d 100%); border-radius: 9999px; box-shadow: 0 0 8px rgba(244,63,118,0.8);"></div>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 11px;">
                        <div style="display: flex; align-items: center; gap: 8px; color: #6ee7b7;">
                            <span>✓</span>
                            <span style="color: #fce7f3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Processing 24 emails</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; color: #6ee7b7;">
                            <span>✓</span>
                            <span style="color: #fce7f3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Summarizing client report</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; color: #fce7f3;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="width: 7px; height: 7px; border-radius: 50%; background: #a855f7;"></span> Updating tracker
                            </span>
                            <span style="font-size: 9px; color: #d8b4fe; background: rgba(59, 7, 100, 0.6); border: 1px solid #6b21a8; padding: 2px 6px; border-radius: 4px;">In progress</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; color: #a88094;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="width: 7px; height: 7px; border-radius: 50%; background: #3f172e;"></span> Calendar sync
                            </span>
                            <span style="font-size: 9px; color: #a88094; background: #1a0b12; border: 1px solid #2b101f; padding: 2px 6px; border-radius: 4px;">Queued</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; color: #a88094;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="width: 7px; height: 7px; border-radius: 50%; background: #3f172e;"></span> Document analysis
                            </span>
                            <span style="font-size: 9px; color: #a88094; background: #1a0b12; border: 1px solid #2b101f; padding: 2px 6px; border-radius: 4px;">Queued</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sub2:
            st.markdown(
                f"""
                <div style="background: rgba(35, 12, 24, 0.7); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 16px; height: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.15); display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="color: #fb719e;">◈</span>
                                <span>Productivity Snapshot</span>
                            </span>
                            <span style="font-size: 10px; color: #a88094; cursor: pointer;">This Week ▼</span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-bottom: 12px;">
                            <div style="background: rgba(26, 11, 18, 0.8); border: 1px solid rgba(43, 16, 31, 0.6); border-radius: 12px; padding: 8px 4px;">
                                <span style="color: #fb719e; font-size: 12px; margin-bottom: 2px; display: block;">◇</span>
                                <span style="font-size: 14px; font-weight: 700; color: #ffffff; display: block;">{metrics['emails_sent']}</span>
                                <span style="font-size: 9px; color: #a88094; display: block;">Emails Sent</span>
                                <span style="font-size: 8px; color: #34d399; font-weight: 600;">↑ 12%</span>
                            </div>
                            <div style="background: rgba(26, 11, 18, 0.8); border: 1px solid rgba(43, 16, 31, 0.6); border-radius: 12px; padding: 8px 4px;">
                                <span style="color: #fb719e; font-size: 12px; margin-bottom: 2px; display: block;">✓</span>
                                <span style="font-size: 14px; font-weight: 700; color: #ffffff; display: block;">{metrics['completed']}</span>
                                <span style="font-size: 9px; color: #a88094; display: block;">Tasks Done</span>
                                <span style="font-size: 8px; color: #34d399; font-weight: 600;">↑ 25%</span>
                            </div>
                            <div style="background: rgba(26, 11, 18, 0.8); border: 1px solid rgba(43, 16, 31, 0.6); border-radius: 12px; padding: 8px 4px;">
                                <span style="color: #fb719e; font-size: 12px; margin-bottom: 2px; display: block;">◈</span>
                                <span style="font-size: 14px; font-weight: 700; color: #ffffff; display: block;">{metrics['events_today']}</span>
                                <span style="font-size: 9px; color: #a88094; display: block;">Meetings</span>
                                <span style="font-size: 8px; color: #34d399; font-weight: 600;">↑ 20%</span>
                            </div>
                        </div>
                    </div>
                    <div style="background: rgba(20, 6, 13, 0.6); border-radius: 12px; padding: 8px; text-align: center; border: 1px solid rgba(43, 16, 31, 0.4);">
                        <p style="font-size: 10px; color: #fce7f3; font-style: italic; margin: 0;">
                            <span style="color: #fb719e; font-style: normal;">✦</span> "Consistency builds momentum."
                        </p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sub3:
            st.markdown(
                """
                <div style="background: rgba(35, 12, 24, 0.7); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 16px; height: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <span style="color: #fb719e;">✦</span>
                            <span>AI Suggested Next</span>
                        </span>
                        <span style="width: 16px; height: 16px; border-radius: 50%; background: rgba(190, 18, 76, 0.6); border: 1px solid #f43f76; font-size: 10px; display: flex; align-items: center; justify-content: center; color: #ffffff; font-weight: 700;">3</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="padding: 8px; border-radius: 12px; background: rgba(26, 11, 18, 0.8); border: 1px solid rgba(43, 16, 31, 0.6); cursor: pointer;">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 12px; color: #fb719e;">◲</span>
                                    <p style="font-size: 11px; color: #ffffff; font-weight: 500; margin: 0;">Summarize today's meeting notes</p>
                                </div>
                                <span style="font-size: 10px; color: #a88094;">&gt;</span>
                            </div>
                            <span style="font-size: 9px; color: #a88094; margin-left: 20px; display: block;">from 11 AM</span>
                        </div>
                        <div style="padding: 8px; border-radius: 12px; background: rgba(26, 11, 18, 0.8); border: 1px solid rgba(43, 16, 31, 0.6); cursor: pointer;">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 12px; color: #fb719e;">◇</span>
                                    <p style="font-size: 11px; color: #ffffff; font-weight: 500; margin: 0;">Follow up with client on proposal</p>
                                </div>
                                <span style="font-size: 10px; color: #a88094;">&gt;</span>
                            </div>
                            <span style="font-size: 9px; color: #a88094; margin-left: 20px; display: block;">pending proposal</span>
                        </div>
                        <div style="padding: 8px; border-radius: 12px; background: rgba(26, 11, 18, 0.8); border: 1px solid rgba(43, 16, 31, 0.6); cursor: pointer;">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 12px; color: #fb719e;">◈</span>
                                    <p style="font-size: 11px; color: #ffffff; font-weight: 500; margin: 0;">Prepare weekly progress report</p>
                                </div>
                                <span style="font-size: 10px; color: #a88094;">&gt;</span>
                            </div>
                            <span style="font-size: 9px; color: #a88094; margin-left: 20px; display: block;">(using last 7 days data)</span>
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
            <div style="background: rgba(35, 12, 24, 0.6); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 20px; box-shadow: 0 8px 24px rgba(20, 6, 13, 0.3); margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(43, 16, 31, 0.6); padding-bottom: 12px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #fb719e; font-size: 16px;">◇</span>
                        <h3 style="font-size: 14px; font-weight: 700; color: #ffffff; margin: 0;">Email Studio &amp; Templates</h3>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 16px; font-size: 12px; font-weight: 500; border-bottom: 1px solid rgba(43, 16, 31, 0.4); padding-bottom: 8px; margin-bottom: 14px;">
                    <span style="color: #ffffff; border-bottom: 2px solid #f43f76; padding-bottom: 6px; font-weight: 600;">Templates</span>
                    <span style="color: #a88094; cursor: pointer;">Automation Toolkits</span>
                    <span style="color: #a88094; cursor: pointer;">Command Center Logs</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #a88094; text-transform: uppercase; letter-spacing: 0.08em;">Popular Templates</span>
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
            <div style="background: rgba(35, 12, 24, 0.7); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <span style="color: #fb719e;">◈</span>
                        <span>Today's Schedule</span>
                    </span>
                    <span style="font-size: 10px; color: #a88094; cursor: pointer;">View Calendar →</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 12px; position: relative;">
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 2px solid #be124c; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #a88094; display: block;">09:00 AM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Daily Engineering Standup</p>
                            <p style="font-size: 10px; color: #a88094; margin: 0;">30 mins · Team sync</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 9999px;">Live</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 2px solid #3f172e; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #a88094; display: block;">11:00 AM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Sprint Planning &amp; Architecture</p>
                            <p style="font-size: 10px; color: #a88094; margin: 0;">1 hour · Google Meet</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: #1a0b12; color: #a88094; border: 1px solid #2b101f; border-radius: 9999px;">Upcoming</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 2px solid #3f172e; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #a88094; display: block;">02:00 PM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Client Demonstration</p>
                            <p style="font-size: 10px; color: #a88094; margin: 0;">1 hour · Live feature walk</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: #1a0b12; color: #a88094; border: 1px solid #2b101f; border-radius: 9999px;">Upcoming</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-left: 2px solid #3f172e; padding-left: 10px;">
                        <div>
                            <span style="font-size: 10px; font-family: monospace; color: #a88094; display: block;">04:30 PM</span>
                            <p style="font-size: 12px; font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Review &amp; Deliverables Wrap-up</p>
                            <p style="font-size: 10px; color: #a88094; margin: 0;">30 mins · Summary</p>
                        </div>
                        <span style="padding: 2px 8px; font-size: 9px; font-weight: 600; background: #1a0b12; color: #a88094; border: 1px solid #2b101f; border-radius: 9999px;">Upcoming</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 2: Recent Activity
        st.markdown(
            """
            <div style="background: rgba(35, 12, 24, 0.7); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <span style="color: #fb719e;">◈</span>
                        <span>Recent Activity</span>
                    </span>
                    <span style="font-size: 10px; color: #a88094; cursor: pointer;">View All →</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 11px;">
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-bottom: 1px solid rgba(43, 16, 31, 0.4); padding-bottom: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #34d399; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Email dispatched to Chetan</p>
                                <p style="font-size: 10px; color: #a88094; margin: 0;">Project update and next steps</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #a88094;">10:30 AM</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-bottom: 1px solid rgba(43, 16, 31, 0.4); padding-bottom: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #c084fc; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Document summary synthesized</p>
                                <p style="font-size: 10px; color: #a88094; margin: 0;">Q1_Report.pdf (4 takeaways)</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #a88094;">09:15 AM</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; border-bottom: 1px solid rgba(43, 16, 31, 0.4); padding-bottom: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #fbbf24; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Meeting scheduled</p>
                                <p style="font-size: 10px; color: #a88094; margin: 0;">Team sync on 24 May, 11:00 AM</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #a88094;">09:00 AM</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;">
                        <div style="display: flex; align-items: flex-start; gap: 8px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: #60a5fa; margin-top: 4px;"></span>
                            <div>
                                <p style="font-weight: 600; color: #ffffff; line-height: 1.2; margin: 0;">Data extracted from sales.xlsx</p>
                                <p style="font-size: 10px; color: #a88094; margin: 0;">5 tables &amp; 2 charts generated</p>
                            </div>
                        </div>
                        <span style="font-size: 9px; font-family: monospace; color: #a88094;">Yesterday</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 3: Voice Command Engine
        st.markdown(
            """
            <div style="background: rgba(35, 12, 24, 0.7); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); text-align: center; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <svg style="width: 16px; height: 16px; color: #fb719e;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"></path></svg>
                        <span>Voice Command Engine</span>
                    </span>
                    <span style="padding: 2px 8px; border-radius: 9999px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; font-size: 9px; font-weight: 500;">
                        ● Listening
                    </span>
                </div>
                <div style="height: 40px; display: flex; align-items: center; justify-content: center; gap: 6px; margin: 8px 0;">
                    <span class="wave-bar" style="width: 4px; background: #fb719e; border-radius: 9999px; height: 12px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #f43f76; border-radius: 9999px; height: 22px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #ff4d8d; border-radius: 9999px; height: 18px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #fb719e; border-radius: 9999px; height: 30px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #f43f76; border-radius: 9999px; height: 14px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #ff4d8d; border-radius: 9999px; height: 26px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #fb719e; border-radius: 9999px; height: 20px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #f43f76; border-radius: 9999px; height: 16px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #ff4d8d; border-radius: 9999px; height: 28px;"></span>
                    <span class="wave-bar" style="width: 4px; background: #fb719e; border-radius: 9999px; height: 10px;"></span>
                </div>
                <p style="font-size: 10px; color: #a88094; margin-bottom: 12px;">Tap to speak or say "Hey ENMA"</p>
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
            <div style="position: relative; background: rgba(35, 12, 24, 0.8); border: 1px solid rgba(43, 16, 31, 0.8); border-radius: 16px; padding: 14px; display: flex; align-items: center; justify-content: space-between; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-top: 8px;">
                <div class="footer-wave"></div>
                <div style="display: flex; align-items: center; gap: 10px; position: relative; z-index: 10;">
                    <span style="font-size: 16px; color: #34d399;">✦</span>
                    <div style="line-height: 1.1;">
                        <p style="font-size: 12px; font-weight: 600; color: #ffffff; margin: 0;">Your workspace is running smoothly</p>
                        <p style="font-size: 10px; color: #a88094; margin: 0;">All systems operational · 99.9% uptime</p>
                    </div>
                </div>
                <span style="color: #a88094; font-size: 12px; position: z-index: 10;">&gt;</span>
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
