"""
ENMA Master Sidebar Navigation Component.
Exact Wine/Plum/Ruby Glassmorphic Palette & Layout from designe/code.html.
"""

from __future__ import annotations
import streamlit as st

MENU_ITEMS = [
    ("Home", "dashboard"),
    ("Email Studio", "tasks"),
    ("Calendar & Events", "calendar"),
    ("Document & Data Studio", "documents"),
    ("Notes & Knowledge", "notes"),
    ("Task & Email Studio", "tasks"),
]

SYSTEM_ITEMS = [
    ("Voice Assistant", "voice"),
    ("Command Center & Settings", "settings"),
]

def render_enma_sidebar(active_view: str) -> str:
    """Renders the exact wine/plum/ruby sidebar from designe/code.html."""
    with st.sidebar:
        # App Brand Logo
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding: 6px 8px 16px 8px;">
                <div style="width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; color: #fb719e;">
                    <svg style="width: 24px; height: 24px; fill: currentColor; filter: drop-shadow(0 0 8px rgba(244,63,118,0.7));" viewBox="0 0 24 24">
                        <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"></path>
                    </svg>
                </div>
                <div style="line-height: 1.1;">
                    <h1 style="font-size: 14px; font-weight: 700; letter-spacing: 0.05em; color: #ffffff; text-transform: uppercase; margin: 0;">ENMA</h1>
                    <p style="font-size: 10px; letter-spacing: 0.15em; color: #a88094; font-weight: 500; text-transform: uppercase; margin: 0;">by LUCORA</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = active_view

        current_normalized = active_view
        if active_view in ("assistant", "voice_commands"):
            current_normalized = "tasks" if active_view == "assistant" else "voice"
        elif active_view in ("files", "data"):
            current_normalized = "documents"
        elif active_view in ("journals", "bookmarks"):
            current_normalized = "notes"
        elif active_view in ("terminal", "integrations"):
            current_normalized = "settings"

        # Main Navigation
        for label, view_key in MENU_ITEMS:
            is_active = (current_normalized == view_key and not (view_key == "tasks" and label.startswith("Task")))
            prefix = "✦ " if is_active else ""
            if st.button(
                f"{prefix}{label}",
                key=f"sidebar_nav_{view_key}_{label[:4]}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected = view_key

        # System & Engine Section
        st.markdown(
            """
            <div style="padding-top: 14px; margin-top: 10px; border-top: 1px solid rgba(43, 16, 31, 0.6);">
                <div style="padding-left: 10px; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; color: rgba(168, 128, 148, 0.7); text-transform: uppercase; margin-bottom: 6px;">
                    SYSTEM &amp; ENGINE
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for label, view_key in SYSTEM_ITEMS:
            is_active = (current_normalized == view_key)
            prefix = "✦ " if is_active else ""
            if st.button(
                f"{prefix}{label}",
                key=f"sidebar_sys_{view_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected = view_key

        # ENMA Pro Banner & User Card
        st.markdown(
            """
            <div style="position: relative; margin-top: 20px; padding: 14px; border-radius: 16px; background: rgba(35, 12, 24, 0.9); border: 1px solid rgba(244, 63, 118, 0.2); box-shadow: 0 4px 20px rgba(20, 6, 13, 0.5);">
                <div style="display: flex; align-items: center; gap: 6px; color: #fb719e; font-weight: 600; font-size: 12px; margin-bottom: 4px;">
                    <svg style="width: 14px; height: 14px; fill: currentColor;" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                    <span style="letter-spacing: 0.05em;">ENMA PRO</span>
                </div>
                <p style="font-size: 11px; color: #a88094; line-height: 1.4; margin-bottom: 10px;">
                    Unlock advanced features, more AI models &amp; higher limits.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Upgrade Plan →", key="btn_upgrade_sidebar_exact", use_container_width=True, type="primary"):
            st.toast("ENMA Pro plan activation link ready", icon="✦")

        # User Profile Card
        st.markdown(
            """
            <div style="margin-top: 14px; display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border-radius: 12px; background: rgba(35, 12, 24, 0.4); border: 1px solid rgba(43, 16, 31, 0.4);">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #be124c 0%, #ff4d8d 100%); display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 12px; font-weight: 700; box-shadow: 0 0 8px rgba(244,63,118,0.4);">
                        VD
                    </div>
                    <div style="line-height: 1.1; overflow: hidden;">
                        <h3 style="font-size: 12px; font-weight: 600; color: #ffffff; margin: 0; white-space: nowrap;">Hriday Gupta</h3>
                        <p style="font-size: 10px; color: #a88094; margin: 0; white-space: nowrap;">hriday.code1119@gmail.com</p>
                    </div>
                </div>
                <div style="color: #a88094; font-size: 14px;">•••</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected

# Backward compatibility aliases
render_lucora_sidebar = render_enma_sidebar
render_aira_sidebar = render_enma_sidebar
