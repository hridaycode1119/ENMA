"""
LUCORA Master Sidebar Navigation Component.
Streamlined, aesthetic, uncluttered navigation matching high-end design systems.
Brand tagline: "Intelligence That Gets Work Done"
"""

from __future__ import annotations
import streamlit as st

MENU_STRUCTURE = {
    "OVERVIEW": [
        ("Dashboard", "dashboard"),
    ],
    "PRODUCTIVITY & ACTIONS": [
        ("Task & Email Studio", "tasks"),
        ("Calendar & Events", "calendar"),
        ("Document & Data Studio", "documents"),
        ("Notes & Knowledge", "notes"),
    ],
    "SYSTEM & ENGINE": [
        ("Voice Assistant", "voice"),
        ("Command Center & Settings", "settings"),
    ],
}

def render_lucora_sidebar(active_view: str) -> str:
    """Renders the sleek, uncluttered LUCORA sidebar navigation."""
    with st.sidebar:
        # 1. Brand Logo & Identity
        st.markdown(
            """
            <div class="sidebar-brand-box">
                <div class="sidebar-logo-badge">✦</div>
                <div>
                    <div class="sidebar-title">LUCORA</div>
                    <div class="sidebar-tagline">Intelligence That Gets Work Done</div>
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

        # 2. Categorized Sections
        for category, items in MENU_STRUCTURE.items():
            st.markdown(f"<div class='sidebar-section-label'>{category}</div>", unsafe_allow_html=True)
            for label, view_key in items:
                is_active = (current_normalized == view_key)
                if st.button(
                    label,
                    key=f"btn_nav_{view_key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    selected = view_key

        # 3. Minimalist Pro Badge Card
        st.markdown(
            """
            <div style="margin-top: 1.5rem; padding: 0.9rem; border-radius: 12px; background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%); border: 1px solid #ddd6fe;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #4f46e5; display: flex; align-items: center; gap: 0.35rem;">
                    <span>✦</span> LUCORA Pro
                </div>
                <div style="font-size: 0.72rem; color: #64748b; margin: 0.25rem 0 0.5rem 0; line-height: 1.4;">
                    Full reasoning power, unlimited tools & cloud database sync.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Upgrade Plan →", key="btn_upgrade_pro", use_container_width=True):
            st.toast("LUCORA Pro plan activation link generated", icon="✦")

        # 4. Clean User Profile Footer
        st.markdown(
            """
            <div class="user-card-clean">
                <div class="user-avatar-circle">VD</div>
                <div style="overflow: hidden;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #0f172a; white-space: nowrap; text-overflow: ellipsis;">Vaishnavi Dhyani</div>
                    <div style="font-size: 0.7rem; color: #94a3b8; white-space: nowrap; text-overflow: ellipsis;">vaishnavi.d@example.com</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected

# Backward-compatibility alias
render_aira_sidebar = render_lucora_sidebar
