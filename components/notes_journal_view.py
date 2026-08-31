"""
AIRA Notes, Journals, and Bookmarks Views.
Persisted via AIRARepository and Supabase PostgreSQL.
"""

from __future__ import annotations
import streamlit as st
import datetime
from database.repository import AIRARepository

def render_notes_view() -> None:
    st.markdown("### 📑 Notes & Ideas")
    st.caption("Quick scratchpad and persistent research notes synced with Supabase.")

    repo = AIRARepository()
    notes = repo.get_notes(category="note")

    n_col1, n_col2 = st.columns([5, 4])
    with n_col1:
        if not notes:
            st.info("No notes found. Create your first note on the right!")
        for idx, note in enumerate(notes):
            with st.container(border=True):
                st.markdown(f"**{note.get('title', 'Untitled')}**")
                st.caption(f"📅 {note.get('date_str', 'Recently')}")
                st.text(note.get("content", ""))

    with n_col2:
        with st.form(key="add_note_form"):
            st.markdown("#### ➕ Add New Note")
            nt_title = st.text_input("Note Title")
            nt_content = st.text_area("Note Body", height=120)
            if st.form_submit_button("💾 Save Note", type="primary", use_container_width=True):
                if nt_title:
                    repo.save_note(
                        title=nt_title,
                        content=nt_content,
                        category="note",
                        date_str=datetime.date.today().strftime("%d %b %Y"),
                    )
                    st.toast("Note saved to database", icon="💾")
                    st.rerun()

def render_journals_view() -> None:
    st.markdown("### 📖 Daily Work Journals")
    st.caption("Engineering work logs and task summaries synced with Supabase.")

    repo = AIRARepository()
    journals = repo.get_notes(category="journal")

    if not journals:
        default_journals = [
            ("21 May 2025", "Worked on project automation, email integration, AIRA dashboard UI, and Supabase backend."),
            ("20 May 2025", "Researched file data extraction, PDF editing, and AI tools for enterprise document processing."),
            ("19 May 2025", "Implemented OAuth 2.0 PKCE authorization manager with token caching."),
        ]
        for d, c in default_journals:
            repo.save_note(title=d, content=c, category="journal", date_str=d)
        journals = repo.get_notes(category="journal")

    for entry in journals:
        with st.container(border=True):
            st.markdown(f"**{entry.get('title', entry.get('date_str'))}**")
            st.markdown(entry.get("content", ""))

def render_bookmarks_view() -> None:
    st.markdown("### 🔖 Quick Bookmarks & Resources")
    st.caption("Pinned developer documentation and cloud consoles.")

    bookmarks = [
        ("OpenAI API Documentation", "https://platform.openai.com/docs", "Official API references and models."),
        ("Google Gmail API Quickstart", "https://developers.google.com/gmail/api", "Google Workspace REST APIs."),
        ("Supabase Cloud Dashboard", "https://supabase.com/dashboard", "PostgreSQL database & auth management console."),
        ("Streamlit Documentation", "https://docs.streamlit.io", "Python web application framework docs."),
    ]
    for title, url, desc in bookmarks:
        with st.container(border=True):
            col_info, col_link = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{title}**")
                st.caption(f"{desc} • `{url}`")
            with col_link:
                st.link_button("🌐 Open Link", url, use_container_width=True)
