"""
ENMA Enterprise Team & Directory Component.
Provides interactive enterprise member cards, registration of new members,
and 1-click contacting actions (Direct Email, Schedule Meeting, Quick Note).
"""

from __future__ import annotations
import streamlit as st
from typing import Optional, Callable

from database.repository import ENMARepository

def render_team_view(on_navigate_view: Optional[Callable[[str], None]] = None) -> None:
    """Renders the comprehensive Enterprise Team Directory & Management View."""
    repo = ENMARepository()
    members = repo.get_team_members()

    # 1. Header Banner
    st.markdown(
        """
        <div style="position: relative; border-radius: 16px; background: linear-gradient(135deg, #230c18 0%, #2c0e1e 50%, #2b101f 100%); border: 1px solid rgba(244, 63, 118, 0.25); padding: 22px; overflow: hidden; box-shadow: 0 10px 30px rgba(20, 6, 13, 0.4); margin-bottom: 20px;">
            <div class="hero-wave"></div>
            <div style="position: relative; z-index: 10;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="color: #fb719e; font-size: 22px;">👥</span>
                    <h2 style="font-size: 24px; font-weight: 700; letter-spacing: -0.01em; color: #ffffff; margin: 0;">Enterprise Team Directory</h2>
                </div>
                <p style="font-size: 12px; color: rgba(252, 231, 243, 0.8); max-width: 680px; line-height: 1.5; margin: 0;">
                    Manage enterprise collaborators, assign AI workflows, launch 1-click email dispatches, and schedule meetings.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Metric Snapshot Row
    active_count = sum(1 for m in members if m.get("status") in ("Active", "Available"))
    in_meeting_count = sum(1 for m in members if m.get("status") == "In Meeting")
    depts = set(m.get("department", "Engineering") for m in members)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(
            f"""
            <div style="background: rgba(35, 12, 24, 0.85); border: 1px solid rgba(63, 23, 46, 0.9); border-radius: 14px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(20, 6, 13, 0.3);">
                <span style="color: #fb719e; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 4px;">Total Members</span>
                <span style="font-size: 24px; font-weight: 800; color: #ffffff;">{len(members)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            f"""
            <div style="background: rgba(35, 12, 24, 0.85); border: 1px solid rgba(63, 23, 46, 0.9); border-radius: 14px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(20, 6, 13, 0.3);">
                <span style="color: #34d399; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 4px;">Available Now</span>
                <span style="font-size: 24px; font-weight: 800; color: #ffffff;">{active_count}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            f"""
            <div style="background: rgba(35, 12, 24, 0.85); border: 1px solid rgba(63, 23, 46, 0.9); border-radius: 14px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(20, 6, 13, 0.3);">
                <span style="color: #fbbf24; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 4px;">In Meetings</span>
                <span style="font-size: 24px; font-weight: 800; color: #ffffff;">{in_meeting_count}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            f"""
            <div style="background: rgba(35, 12, 24, 0.85); border: 1px solid rgba(63, 23, 46, 0.9); border-radius: 14px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(20, 6, 13, 0.3);">
                <span style="color: #c084fc; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 4px;">Departments</span>
                <span style="font-size: 24px; font-weight: 800; color: #ffffff;">{len(depts)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 3. Controls & Add Member Form
    col_search, col_dept, col_add_btn = st.columns([3, 2, 2])
    with col_search:
        search_q = st.text_input("Search Team", placeholder="Search by name, role, or email...", label_visibility="collapsed", key="team_search_query")
    with col_dept:
        dept_filter = st.selectbox(
            "Department Filter",
            ["All Departments"] + sorted(list(depts)),
            label_visibility="collapsed",
            key="team_dept_filter",
        )
    with col_add_btn:
        show_add = st.checkbox("✦ Add Member", key="team_toggle_add_form")

    if show_add:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 14px; font-weight: 700; color: #ffffff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <span style="color: #fb719e;">✦</span>
                    <span>Register New Enterprise Team Member</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("form_add_team_member", clear_on_submit=True):
                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    new_name = st.text_input("Full Name*", placeholder="e.g., Jane Doe")
                    new_email = st.text_input("Enterprise Email*", placeholder="e.g., jane.doe@enterprise.com")
                    new_role = st.text_input("Role / Title*", placeholder="e.g., AI Research Scientist")
                with f_c2:
                    new_dept = st.selectbox(
                        "Department*",
                        ["AI Engineering", "Engineering", "Product", "Security", "Design", "Operations", "Legal", "Executive"],
                    )
                    new_phone = st.text_input("Phone Number", placeholder="e.g., +91 98765 00000")
                    new_status = st.selectbox("Current Status", ["Active", "Available", "In Meeting", "Away"])

                submitted = st.form_submit_button("✦ Register Member →", type="primary", use_container_width=True)
                if submitted:
                    if not new_name or not new_email or not new_role:
                        st.error("Please fill in all required fields (Name, Email, Role).")
                    elif "@" not in new_email:
                        st.error("Please provide a valid email address.")
                    else:
                        repo.add_team_member(
                            name=new_name,
                            email=new_email,
                            role=new_role,
                            department=new_dept,
                            phone=new_phone,
                            status=new_status,
                        )
                        st.success(f"Team member '{new_name}' registered successfully!")
                        st.toast(f"Added {new_name} to enterprise directory", icon="✦")
                        st.rerun()

    # 4. Filter Members
    filtered = members
    if search_q:
        q_lower = search_q.strip().lower()
        filtered = [
            m for m in filtered
            if q_lower in m.get("name", "").lower() or q_lower in m.get("email", "").lower() or q_lower in m.get("role", "").lower()
        ]
    if dept_filter and dept_filter != "All Departments":
        filtered = [m for m in filtered if m.get("department") == dept_filter]

    st.write("")

    if not filtered:
        st.info("No team members match the search criteria.")
        return

    # 5. Member Cards (2 per row, rendered inside seamless dark wine containers)
    for i in range(0, len(filtered), 2):
        row_members = filtered[i:i+2]
        cols = st.columns(2)
        for c_idx, member in enumerate(row_members):
            with cols[c_idx]:
                with st.container(border=True):
                    m_id = member.get("id", f"mem_{i+c_idx}")
                    m_name = member.get("name", "Team Member")
                    m_email = member.get("email", "user@enterprise.com")
                    m_role = member.get("role", "Engineer")
                    m_dept = member.get("department", "Engineering")
                    m_status = member.get("status", "Active")
                    m_phone = member.get("phone", "+91 98765 00000")
                    m_init = member.get("initials", m_name[:2].upper())
                    m_color = member.get("color", "#be124c")

                    status_color = "#34d399" if m_status in ("Active", "Available") else "#fbbf24" if m_status == "In Meeting" else "#a88094"

                    st.markdown(
                        f"""
                        <div style="margin-bottom: 12px;">
                            <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px;">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, {m_color} 0%, #ff4d8d 100%); display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 15px; font-weight: 700; box-shadow: 0 0 12px rgba(244,63,118,0.4); flex-shrink: 0;">
                                        {m_init}
                                    </div>
                                    <div>
                                        <div style="display: flex; align-items: center; gap: 8px;">
                                            <h3 style="font-size: 15px; font-weight: 700; color: #ffffff; margin: 0;">{m_name}</h3>
                                            <span style="font-size: 9px; font-weight: 600; padding: 2px 8px; border-radius: 9999px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #fce7f3;">{m_dept}</span>
                                        </div>
                                        <p style="font-size: 11px; color: #fb719e; font-weight: 500; margin: 2px 0 0 0;">{m_role}</p>
                                    </div>
                                </div>
                                <div style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: 9999px; background: rgba(20, 6, 13, 0.8); border: 1px solid rgba(43, 16, 31, 0.9); font-size: 10px;">
                                    <span style="width: 6px; height: 6px; border-radius: 50%; background: {status_color}; box-shadow: 0 0 6px {status_color};"></span>
                                    <span style="color: #ffffff; font-weight: 500;">{m_status}</span>
                                </div>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: #a88094; padding-left: 56px;">
                                <div><span style="color: #fb719e;">✉</span> <span style="color: #fce7f3; font-family: monospace;">{m_email}</span></div>
                                <div><span style="color: #fb719e;">📞</span> <span style="color: #fce7f3; font-family: monospace;">{m_phone}</span></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Contacting Action Buttons Row (Embedded directly inside card)
                    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)
                    with btn_c1:
                        if st.button("◇ Email", key=f"btn_contact_email_{m_id}", use_container_width=True, help=f"Compose email to {m_name}"):
                            st.session_state["main_email_to"] = m_email
                            st.session_state["dash_exact_email_to"] = m_email
                            st.session_state["email_to"] = m_email
                            st.session_state["main_email_subject"] = f"Sync with {m_name}"
                            st.toast(f"Prepared Email Composer for {m_name}", icon="✦")
                            if on_navigate_view:
                                on_navigate_view("tasks")
                            else:
                                st.session_state["enma_active_view"] = "tasks"
                                st.rerun()

                    with btn_c2:
                        if st.button("◈ Meet", key=f"btn_contact_meet_{m_id}", use_container_width=True, help=f"Schedule meeting with {m_name}"):
                            st.session_state["cal_invite_attendee"] = m_email
                            st.toast(f"Opening Calendar for meeting with {m_name}", icon="✦")
                            if on_navigate_view:
                                on_navigate_view("calendar")
                            else:
                                st.session_state["enma_active_view"] = "calendar"
                                st.rerun()

                    with btn_c3:
                        if st.button("◲ Note", key=f"btn_contact_note_{m_id}", use_container_width=True, help=f"Save note about {m_name}"):
                            repo.save_note(
                                title=f"Collaboration Notes: {m_name}",
                                content=f"Contact: {m_email} | {m_phone}\nRole: {m_role} ({m_dept})\nStatus: {m_status}\n\nTopics to discuss:\n• ",
                                category="note",
                            )
                            st.toast(f"Created draft note for {m_name}", icon="✦")

                    with btn_c4:
                        if st.button("⎋ Del", key=f"btn_remove_mem_{m_id}", use_container_width=True, help="Remove member"):
                            if m_email != "hriday.code1119@gmail.com":
                                repo.delete_team_member(m_id)
                                st.toast(f"Removed {m_name}", icon="✦")
                                st.rerun()
                            else:
                                st.error("Cannot delete root lead account.")
