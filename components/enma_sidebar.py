"""
ENMA Master Sidebar Navigation Component.
Wine/Plum/Ruby Glassmorphic Palette, Custom ENMA Nexus Logo & Aesthetic Icons.
"""

from __future__ import annotations
import streamlit as st

MENU_ITEMS = [
    ("✦ Home", "dashboard"),
    ("◇ Email Studio", "tasks"),
    ("◈ Calendar & Events", "calendar"),
    ("⬡ Document & Data Studio", "documents"),
    ("◲ Notes & Knowledge", "notes"),
    ("👥 Enterprise Team", "team"),
]

SYSTEM_ITEMS = [
    ("⍾ Voice Assistant", "voice"),
    ("⎈ Command Center & Settings", "settings"),
]

def render_enma_sidebar(active_view: str) -> str:
    """Renders the sleek, emoji-free ENMA sidebar navigation with cool custom logo."""
    with st.sidebar:
        # App Brand Logo (Bespoke ENMA Hyper-Nexus Logo)
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; padding: 6px 8px 18px 8px;">
                <div style="width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;">
                    <svg style="width: 32px; height: 32px; filter: drop-shadow(0 0 10px rgba(244,63,118,0.8));" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="enmaLogoGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#ff4d8d"/>
                                <stop offset="50%" stop-color="#f43f76"/>
                                <stop offset="100%" stop-color="#be124c"/>
                            </linearGradient>
                        </defs>
                        <circle cx="24" cy="24" r="21" stroke="url(#enmaLogoGlow)" stroke-width="1.5" stroke-dasharray="6 3" opacity="0.6"/>
                        <path d="M24 4L28.5 19.5L44 24L28.5 28.5L24 44L19.5 28.5L4 24L19.5 19.5L24 4Z" fill="url(#enmaLogoGlow)"/>
                        <polygon points="24,11 35,18 35,30 24,37 13,30 13,18" stroke="#ffffff" stroke-width="1.4" fill="none" opacity="0.9"/>
                        <circle cx="24" cy="24" r="3.2" fill="#ffffff"/>
                    </svg>
                </div>
                <div style="line-height: 1.1;">
                    <h1 style="font-size: 15px; font-weight: 800; letter-spacing: 0.08em; color: #ffffff; text-transform: uppercase; margin: 0;">ENMA</h1>
                    <p style="font-size: 10px; letter-spacing: 0.15em; color: #a88094; font-weight: 600; text-transform: uppercase; margin: 0;">ENTERPRISE AI</p>
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

        # Main Navigation Menu
        for label, view_key in MENU_ITEMS:
            is_active = (current_normalized == view_key and not (view_key == "tasks" and "Task" in label))
            if st.button(
                label,
                key=f"sidebar_nav_{view_key}_{label[:3]}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected = view_key

        # System & Engine Section
        st.markdown(
            """
            <div style="padding-top: 14px; margin-top: 10px; border-top: 1px solid rgba(43, 16, 31, 0.6);">
                <div style="padding-left: 8px; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; color: rgba(168, 128, 148, 0.7); text-transform: uppercase; margin-bottom: 6px;">
                    SYSTEM &amp; ENGINE
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for label, view_key in SYSTEM_ITEMS:
            is_active = (current_normalized == view_key)
            if st.button(
                label,
                key=f"sidebar_sys_{view_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected = view_key

        # ENMA Pro Banner
        st.markdown(
            """
            <div style="position: relative; margin-top: 20px; padding: 14px; border-radius: 16px; background: rgba(35, 12, 24, 0.9); border: 1px solid rgba(244, 63, 118, 0.25); box-shadow: 0 4px 20px rgba(20, 6, 13, 0.5);">
                <div style="display: flex; align-items: center; gap: 6px; color: #fb719e; font-weight: 700; font-size: 12px; margin-bottom: 4px;">
                    <span>✦</span>
                    <span style="letter-spacing: 0.05em;">ENMA PRO</span>
                </div>
                <p style="font-size: 11px; color: #a88094; line-height: 1.4; margin-bottom: 10px;">
                    Unlock advanced features, more AI models &amp; higher limits.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Upgrade Plan →", key="btn_upgrade_sidebar_clean", use_container_width=True, type="primary"):
            st.toast("ENMA Pro plan activation link ready")

        # User Profile Card (Hriday Gupta / HG)
        st.markdown(
            """
            <div style="margin-top: 14px; display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border-radius: 12px; background: rgba(35, 12, 24, 0.4); border: 1px solid rgba(43, 16, 31, 0.4);">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #be124c 0%, #ff4d8d 100%); display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 11px; font-weight: 700; box-shadow: 0 0 8px rgba(244,63,118,0.4);">
                        HG
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
