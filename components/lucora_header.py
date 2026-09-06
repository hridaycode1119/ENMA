"""
LUCORA Top Header Bar Component.
Clean, modern header with greeting, brand tagline 'Intelligence That Gets Work Done',
search bar, notifications badge, voice trigger, and New Task launcher.
"""

from __future__ import annotations
import streamlit as st

def render_lucora_header(on_new_task_click=None) -> None:
    """Renders the clean, aesthetic top header bar."""
    col_greeting, col_actions = st.columns([5, 5])

    with col_greeting:
        st.markdown(
            """
            <div style="padding: 0.2rem 0;">
                <h1 class="lucora-greeting-title">Good morning, Vaishnavi</h1>
                <div class="lucora-tagline-badge">
                    <span>✦</span> <strong>LUCORA</strong> &nbsp;•&nbsp; <span>Intelligence That Gets Work Done</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_actions:
        search_col, mic_col, notif_col, btn_col = st.columns([5, 1, 1, 3])
        with search_col:
            st.text_input(
                "Search",
                placeholder="Search or ask anything... ⌘ K",
                label_visibility="collapsed",
                key="global_search_input",
            )
        with mic_col:
            if st.button("🎙", key="header_mic_btn", help="Voice Command Input"):
                st.session_state["lucora_voice_listening"] = True
                st.toast("Listening for voice command...", icon="🎙")
        with notif_col:
            if st.button("🔔", key="header_notif_btn", help="3 Unread Notifications"):
                st.toast("3 Notifications: 1 Task due, 1 Email draft ready, 1 Meeting soon.", icon="🔔")
        with btn_col:
            if st.button("＋ New Task", key="header_new_task_btn", type="primary", use_container_width=True):
                if on_new_task_click:
                    on_new_task_click()
                else:
                    st.session_state["lucora_active_view"] = "dashboard"
                    st.toast("Opened Command Console", icon="✦")

    st.write("")

# Backward-compatibility alias
render_aira_header = render_lucora_header
