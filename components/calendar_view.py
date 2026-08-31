"""
AIRA Dedicated Calendar & Meeting Scheduling View.
"""

from __future__ import annotations
import streamlit as st
import datetime

from tools.calendar.calendar_tool import CalendarScheduleTool

def render_calendar_view() -> None:
    """Renders the full Calendar & Meeting Scheduler workspace."""
    st.markdown("### 📅 Calendar & Meeting Scheduler")
    st.caption("Schedule enterprise meetings, sync with Google Calendar, and generate Google Meet video links.")

    cal_tool = CalendarScheduleTool()
    events = cal_tool.list_today_events()

    col_sched, col_form = st.columns([5, 4])

    with col_sched:
        st.markdown("#### 🕒 Today's Schedule & Agenda")
        for evt in events:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{evt['title']}**")
                    st.caption(f"⏰ {evt['time']} ({evt['duration']}) • 👥 {', '.join(evt.get('attendees', []))}")
                with c2:
                    st.link_button("📹 Join Meet", evt.get("meet_url", "https://meet.google.com"), use_container_width=True)

    with col_form:
        st.markdown("#### ➕ Schedule New Meeting")
        with st.form(key="calendar_schedule_form"):
            meet_title = st.text_input("Meeting Title", placeholder="e.g., Project Sprint Review")
            meet_date = st.date_input("Date", value=datetime.date.today())
            meet_time = st.selectbox("Time Slot", ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:30 PM", "04:30 PM"])
            meet_dur = st.selectbox("Duration", ["15 mins", "30 mins", "45 mins", "1 hour"])
            meet_attendees = st.text_input("Attendees", placeholder="e.g., chetan@enterprise.com, advisor@univ.edu")

            submit = st.form_submit_button("📅 Schedule Meeting", type="primary", use_container_width=True)

            if submit and meet_title:
                res = cal_tool.execute({
                    "title": meet_title,
                    "time": f"{meet_date.strftime('%d %b %Y')}, {meet_time}",
                    "duration": meet_dur,
                    "attendees": [a.strip() for a in meet_attendees.split(",") if a.strip()],
                })
                if res.success:
                    st.success(f"🎉 **Meeting Scheduled!**\n• Link: `{res.data['meet_url']}`\n• Event ID: `{res.data['event_id']}`")
                    st.toast("Meeting added to Google Calendar", icon="📅")
