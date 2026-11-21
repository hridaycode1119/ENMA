"""
ENMA Enterprise Helpdesk & Issue Tickets Component.
Bright, Clean & Light Formal Corporate Palette.
Enables employees and team members to raise, track, and resolve operational friction,
salary/payroll queries, holiday/leave coordination, and company workflow bottlenecks.
"""

from __future__ import annotations
import datetime
from typing import Optional, Callable, Dict, Any, List
import streamlit as st

from database.repository import ENMARepository

CATEGORIES = [
    "Workflow / Operational Bottleneck",
    "Salary / Compensation / Payroll",
    "Holiday / Leave Request",
    "IT & Infrastructure / Hardware",
    "HR & Workplace Relations",
    "Security & Access Permissions",
]

PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]

def render_tickets_view(on_navigate_view: Optional[Callable[[str], None]] = None) -> None:
    """Renders the comprehensive Enterprise Ticket & Helpdesk Management System."""
    repo = ENMARepository()
    stats = repo.get_ticket_stats()
    members = repo.get_team_members()

    # 1. Header Banner (Light Formal Theme)
    st.markdown(
        """
        <div style="position: relative; border-radius: 16px; background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 60%, #e0e7ff 100%); border: 1px solid #bfdbfe; padding: 22px; overflow: hidden; box-shadow: 0 4px 20px rgba(37, 99, 235, 0.08); margin-bottom: 20px;">
            <div class="hero-wave"></div>
            <div style="position: relative; z-index: 10;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <span style="color: #2563eb; font-size: 22px;">🎫</span>
                            <h2 style="font-size: 24px; font-weight: 800; letter-spacing: -0.01em; color: #0f172a; margin: 0;">Enterprise Helpdesk &amp; Workflow Issues</h2>
                        </div>
                        <p style="font-size: 13px; color: #475569; max-width: 680px; line-height: 1.5; margin: 0;">
                            Submit and resolve organizational friction, payroll &amp; salary inquiries, holiday approvals, and operational pipeline bottlenecks.
                        </p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 9999px; background: #ecfdf5; border: 1px solid #a7f3d0; font-size: 11px; color: #047857; font-weight: 700;">
                            <span style="width: 7px; height: 7px; border-radius: 50%; background: #059669; box-shadow: 0 0 6px #059669;"></span>
                            Helpdesk Engine Active
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Metric Snapshot Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                <span style="color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; display: block; margin-bottom: 4px;">Total Tickets</span>
                <span style="font-size: 24px; font-weight: 800; color: #0f172a;">{stats['total']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                <span style="color: #d97706; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; display: block; margin-bottom: 4px;">Open &amp; Pending</span>
                <span style="font-size: 24px; font-weight: 800; color: #b45309;">{stats['open']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                <span style="color: #2563eb; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; display: block; margin-bottom: 4px;">In Progress</span>
                <span style="font-size: 24px; font-weight: 800; color: #1e40af;">{stats['in_progress']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                <span style="color: #059669; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; display: block; margin-bottom: 4px;">Resolved</span>
                <span style="font-size: 24px; font-weight: 800; color: #047857;">{stats['resolved']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 3. Controls & Add Ticket Toggle
    c_search, c_cat, c_status, c_btn = st.columns([3, 2.5, 2, 1.8])
    with c_search:
        search_q = st.text_input(
            "Search Tickets",
            placeholder="Search by title, submitter, department...",
            label_visibility="collapsed",
            key="ticket_search_query",
        )
    with c_cat:
        cat_filter = st.selectbox(
            "Category Filter",
            ["All Categories"] + CATEGORIES,
            label_visibility="collapsed",
            key="ticket_cat_filter",
        )
    with c_status:
        status_filter = st.selectbox(
            "Status Filter",
            ["All Statuses"] + STATUSES,
            label_visibility="collapsed",
            key="ticket_status_filter",
        )
    with c_btn:
        show_raise_form = st.checkbox("✦ Raise Ticket", key="toggle_raise_ticket_form")

    # 4. Ticket Creation Form
    if show_raise_form:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <span style="color: #2563eb;">✦</span>
                    <span>Submit Internal Inconvenience or Workflow Ticket</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Build member choices
            member_options = [f"{m['name']} ({m['department']}) — {m['email']}" for m in members]
            default_member_idx = 0

            with st.form("form_raise_enterprise_ticket", clear_on_submit=True):
                r1_c1, r1_c2 = st.columns(2)
                with r1_c1:
                    selected_emp = st.selectbox("Submitting Employee / Member*", member_options, index=default_member_idx)
                with r1_c2:
                    t_cat = st.selectbox("Issue Category*", CATEGORIES)

                r2_c1, r2_c2 = st.columns([3, 1])
                with r2_c1:
                    t_title = st.text_input("Issue Summary / Title*", placeholder="e.g., Delay in Q3 salary slip adjustment or Git CI/CD workflow blocking release")
                with r2_c2:
                    t_prio = st.selectbox("Priority Level*", PRIORITIES, index=1)

                t_desc = st.text_area(
                    "Detailed Description of the Inconvenience / Bottleneck*",
                    height=120,
                    placeholder="Describe what occurred, which pipeline or department is affected, and any urgency or dates involved...",
                )

                st.caption("💡 *Tickets are routed automatically to Operations, HR, or Engineering leads and encrypted via the Security Vault.*")

                submitted = st.form_submit_button("✦ Submit Ticket to Helpdesk →", type="primary", use_container_width=True)

                if submitted:
                    if not t_title or not t_desc:
                        st.error("Please provide both an issue title and a detailed description.")
                    else:
                        # Extract employee name, department, email
                        emp_parts = selected_emp.split(" — ")
                        emp_email = emp_parts[1].strip() if len(emp_parts) > 1 else "employee@enterprise.com"
                        name_dept = emp_parts[0]
                        emp_name = name_dept.split(" (")[0].strip()
                        emp_dept = name_dept.split(" (")[1].replace(")", "").strip() if "(" in name_dept else "Engineering"

                        new_tkt = repo.create_ticket(
                            title=t_title,
                            category=t_cat,
                            description=t_desc,
                            created_by_name=emp_name,
                            created_by_email=emp_email,
                            department=emp_dept,
                            priority=t_prio,
                        )
                        st.success(f"Ticket #{new_tkt['id']} submitted successfully!")
                        st.toast(f"Ticket #{new_tkt['id']} dispatched to {t_cat}")
                        st.rerun()

    # 5. Fetch and Filter Tickets
    tickets = repo.get_tickets(
        category=cat_filter,
        status=status_filter,
        search_query=search_q,
    )

    st.write("")

    if not tickets:
        st.info("No enterprise tickets match the current filters.")
        return

    # 6. Render Ticket Cards
    for tkt in tickets:
        t_id = tkt.get("id", "tkt-00")
        t_title = tkt.get("title", "Untitled Ticket")
        t_cat = tkt.get("category", "Workflow / Operational Bottleneck")
        t_prio = tkt.get("priority", "Medium")
        t_status = tkt.get("status", "Open")
        t_name = tkt.get("created_by_name", "Employee")
        t_email = tkt.get("created_by_email", "emp@enterprise.com")
        t_dept = tkt.get("department", "Engineering")
        t_desc = tkt.get("description", "")
        t_note = tkt.get("resolution_note", "")
        t_time = tkt.get("created_at", "")[:10]

        # Priority styling
        if t_prio == "Urgent":
            prio_color = "#b91c1c"
            prio_bg = "#fef2f2"
            prio_border = "#fecaca"
        elif t_prio == "High":
            prio_color = "#c2410c"
            prio_bg = "#fff7ed"
            prio_border = "#fed7aa"
        elif t_prio == "Medium":
            prio_color = "#1d4ed8"
            prio_bg = "#eff6ff"
            prio_border = "#bfdbfe"
        else:
            prio_color = "#475569"
            prio_bg = "#f1f5f9"
            prio_border = "#cbd5e1"

        # Status styling
        if t_status == "Resolved":
            stat_color = "#047857"
            stat_bg = "#ecfdf5"
            stat_border = "#a7f3d0"
        elif t_status == "In Progress":
            stat_color = "#1d4ed8"
            stat_bg = "#eff6ff"
            stat_border = "#bfdbfe"
        elif t_status == "Closed":
            stat_color = "#64748b"
            stat_bg = "#f8fafc"
            stat_border = "#e2e8f0"
        else:
            stat_color = "#b45309"
            stat_bg = "#fffbeb"
            stat_border = "#fde68a"

        # Category icon
        cat_icon = "⚡" if "Workflow" in t_cat else "💰" if "Salary" in t_cat else "🗓️" if "Holiday" in t_cat else "💻" if "IT" in t_cat else "👥" if "HR" in t_cat else "🔒"

        with st.container(border=True):
            # Top card row: Title, Category badge, Priority badge, Status pill
            st.markdown(
                f"""
                <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span style="font-family: monospace; font-size: 11px; font-weight: 700; color: #2563eb; background: #eff6ff; border: 1px solid #bfdbfe; padding: 2px 6px; border-radius: 4px;">{t_id}</span>
                            <span style="font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 9999px; background: #f8fafc; border: 1px solid #e2e8f0; color: #334155;">
                                {cat_icon} {t_cat}
                            </span>
                            <span style="font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 9999px; background: {prio_bg}; border: 1px solid {prio_border}; color: {prio_color};">
                                {t_prio} Priority
                            </span>
                        </div>
                        <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 0;">{t_title}</h3>
                    </div>
                    <div>
                        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 9999px; background: {stat_bg}; border: 1px solid {stat_border}; font-size: 11px; font-weight: 700; color: {stat_color};">
                            <span style="width: 7px; height: 7px; border-radius: 50%; background: {stat_color};"></span>
                            {t_status}
                        </span>
                    </div>
                </div>
                <div style="font-size: 13px; color: #334155; line-height: 1.5; margin-bottom: 12px; background: #f8fafc; padding: 10px 14px; border-radius: 8px; border: 1px solid #e2e8f0;">
                    {t_desc}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if t_note:
                st.markdown(
                    f"""
                    <div style="font-size: 12px; color: #047857; background: #ecfdf5; border-left: 3px solid #059669; padding: 6px 12px; border-radius: 4px; margin-bottom: 10px;">
                        <b>Resolution Note:</b> {t_note}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Bottom Submitter Info & Action Buttons Row
            b_info, b_act1, b_act2, b_act3 = st.columns([3, 1.2, 1.2, 1.4])
            with b_info:
                st.markdown(
                    f"""
                    <div style="font-size: 11px; color: #64748b; padding-top: 6px;">
                        <span>Raised by: <b style="color: #0f172a;">{t_name}</b> ({t_dept})</span> &nbsp;·&nbsp;
                        <span style="font-family: monospace;">{t_email}</span> &nbsp;·&nbsp;
                        <span>Date: {t_time}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with b_act1:
                if t_status == "Open":
                    if st.button("⚡ Investigate", key=f"btn_investigate_{t_id}", use_container_width=True):
                        repo.update_ticket_status(t_id, "In Progress")
                        st.toast(f"Ticket #{t_id} marked In Progress")
                        st.rerun()
                elif t_status == "In Progress":
                    if st.button("✓ Resolve", key=f"btn_resolve_quick_{t_id}", use_container_width=True):
                        repo.update_ticket_status(t_id, "Resolved", resolution_note="Action item verified and cleared by workflow administrator.")
                        st.toast(f"Ticket #{t_id} marked Resolved")
                        st.rerun()

            with b_act2:
                if t_status != "Closed":
                    if st.button("⎋ Close", key=f"btn_close_{t_id}", use_container_width=True):
                        repo.update_ticket_status(t_id, "Closed")
                        st.toast(f"Ticket #{t_id} closed")
                        st.rerun()

            with b_act3:
                if st.button("◇ Email Submitter", key=f"btn_mail_submitter_{t_id}", use_container_width=True):
                    st.session_state["main_email_to"] = t_email
                    st.session_state["dash_exact_email_to"] = t_email
                    st.session_state["email_to"] = t_email
                    st.session_state["main_email_subject"] = f"Update regarding Ticket #{t_id}: {t_title}"
                    st.session_state["main_email_body"] = f"Dear {t_name},\n\nWe have reviewed your ticket regarding '{t_title}'.\n\nStatus: {t_status}\n\nNext Steps:\n• "
                    st.toast(f"Prepared Email Composer for {t_name}")
                    if on_navigate_view:
                        on_navigate_view("tasks")
                    else:
                        st.session_state["enma_active_view"] = "tasks"
                        st.rerun()
