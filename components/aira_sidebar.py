"""
AIRA Master Sidebar Navigation Component.
Renders brand logo, categorized navigation menu, Pro upgrade banner, and User Profile.
"""

from __future__ import annotations
import streamlit as st

MENU_STRUCTURE = {
    "MAIN": [
        ("🏠 Dashboard", "dashboard"),
    ],
    "PRODUCTIVITY": [
        ("📝 Task List", "tasks"),
        ("📅 Calendar", "calendar"),
        ("📑 Notes", "notes"),
        ("📖 Journals", "journals"),
        ("🔖 Bookmarks", "bookmarks"),
    ],
    "FILES & DATA": [
        ("📁 File Manager", "files"),
        ("📊 Data Tools", "data"),
        ("📄 Documents", "documents"),
    ],
    "AI TOOLS": [
        ("🤖 AI Assistant", "assistant"),
        ("🎙️ AI Voice Assistant", "voice"),
        ("⚡ Voice Commands", "voice_commands"),
    ],
    "SYSTEM": [
        ("💻 Command Center", "terminal"),
        ("🔗 Integrations", "integrations"),
        ("⚙️ Settings", "settings"),
    ],
}

def render_aira_sidebar(active_view: str) -> str:
    """Renders the comprehensive AIRA sidebar navigation and returns selected view."""
    with st.sidebar:
        # 1. Brand Logo & Identity
        st.markdown(
            """
            <div class="sidebar-brand-header">
                <div class="sidebar-logo-icon">🤖</div>
                <div>
                    <div class="sidebar-brand-title">AIRA</div>
                    <div class="sidebar-brand-sub">AI Agent</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = active_view

        # 2. Main Dashboard Item
        if st.button("🏠 Dashboard", key="btn_nav_dashboard", use_container_width=True, type="primary" if active_view == "dashboard" else "secondary"):
            selected = "dashboard"

        # 3. Categorized Sections
        for category, items in list(MENU_STRUCTURE.items())[1:]:
            st.markdown(f"<div class='sidebar-category-header'>{category}</div>", unsafe_allow_html=True)
            for label, view_key in items:
                is_active = (active_view == view_key)
                if st.button(label, key=f"btn_nav_{view_key}", use_container_width=True, type="primary" if is_active else "secondary"):
                    selected = view_key

        # 4. Upgrade to Pro Card
        st.markdown(
            """
            <div class="upgrade-pro-card">
                <div class="upgrade-title">🚀 Upgrade to Pro</div>
                <div class="upgrade-sub">Unlock advanced AI models, higher tool limits & priority support.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Upgrade Now →", key="btn_upgrade_pro", use_container_width=True):
            st.toast("Pro plan activation link generated!", icon="⭐")

        # 5. User Profile Footer
        st.markdown(
            """
            <div class="user-profile-card">
                <div class="user-avatar">👩‍💻</div>
                <div>
                    <div class="user-name">Vaishnavi Dhyani</div>
                    <div class="user-email">vaishnavi.d@example.com</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected
