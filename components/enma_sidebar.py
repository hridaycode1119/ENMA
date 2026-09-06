"""
ENMA Master Sidebar Navigation Component.
Luxury Dark Wine & Crimson Glassmorphic Design with Wallpaper Backdrop.
"""

from __future__ import annotations
import streamlit as st

MENU_ITEMS = [
    ("🏠 Home", "dashboard"),
    ("✉️ Email Studio", "tasks"),
    ("📅 Calendar & Events", "calendar"),
    ("📄 Document & Data Studio", "documents"),
    ("📖 Notes & Knowledge", "notes"),
    ("⚡ Task & Email Studio", "tasks"),
]

SYSTEM_ITEMS = [
    ("🎙️ Voice Assistant", "voice"),
    ("⚙️ Command Center & Settings", "settings"),
]

def render_enma_sidebar(active_view: str) -> str:
    """Renders the luxury wine & crimson ENMA sidebar navigation."""
    with st.sidebar:
        # 1. Brand Logo Header
        st.markdown(
            """
            <div class="enma-sidebar-brand">
                <div class="enma-brand-spark">✦</div>
                <div>
                    <div class="enma-brand-title">ENMA</div>
                    <div class="enma-brand-sub">by LUCORA</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = active_view

        # Map equivalent view keys
        current_normalized = active_view
        if active_view in ("assistant", "voice_commands"):
            current_normalized = "tasks" if active_view == "assistant" else "voice"
        elif active_view in ("files", "data"):
            current_normalized = "documents"
        elif active_view in ("journals", "bookmarks"):
            current_normalized = "notes"
        elif active_view in ("terminal", "integrations"):
            current_normalized = "settings"

        # 2. Main Navigation Menu
        for label, view_key in MENU_ITEMS:
            is_active = (current_normalized == view_key and not (view_key == "tasks" and label.startswith("⚡")))
            if st.button(
                label,
                key=f"enma_nav_{view_key}_{label[:3]}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected = view_key

        # 3. System & Engine Section
        st.markdown("<div class='enma-sidebar-section'>SYSTEM & ENGINE</div>", unsafe_allow_html=True)
        for label, view_key in SYSTEM_ITEMS:
            is_active = (current_normalized == view_key)
            if st.button(
                label,
                key=f"enma_nav_sys_{view_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected = view_key

        # 4. ENMA Pro Upgrade Card
        st.markdown(
            """
            <div class="enma-pro-card">
                <div class="enma-pro-title">
                    <span style="color: #f43f5e;">⚡</span> ENMA Pro
                </div>
                <div class="enma-pro-desc">
                    Unlock advanced features, more AI models & higher limits.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Upgrade Plan →", key="btn_upgrade_pro_wine", use_container_width=True):
            st.toast("ENMA Pro plan activation link ready", icon="✦")

        # 5. User Profile Card
        st.markdown(
            """
            <div class="enma-user-footer">
                <div class="enma-user-avatar">VD</div>
                <div style="flex: 1; overflow: hidden;">
                    <div class="enma-user-name">Vaishnavi Dhyani</div>
                    <div class="enma-user-email">vaishnavi.d@example.com</div>
                </div>
                <div style="color: #fda4af; font-size: 1.1rem; cursor: pointer;">•••</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected

# Backward-compatibility aliases
render_lucora_sidebar = render_enma_sidebar
render_aira_sidebar = render_enma_sidebar
