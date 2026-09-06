"""
ENMA Top Header Bar Component.
Wine/Plum/Ruby Glassmorphic Palette, Workspace Selector, Omnibox & HG Avatar.
"""

from __future__ import annotations
import streamlit as st

def render_enma_header(on_new_task_click=None) -> None:
    """Renders the sleek, emoji-free ENMA top header bar."""
    col_left, col_mid, col_right = st.columns([3, 6, 2])

    with col_left:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; background: rgba(43, 16, 31, 0.7); color: #ffffff; font-size: 12px; font-weight: 600; padding: 7px 14px; border-radius: 12px; border: 1px solid rgba(63, 23, 46, 0.7); box-shadow: inset 0 1px 2px rgba(0,0,0,0.2); width: fit-content;">
                <svg style="width: 14px; height: 14px; color: #fb719e;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M3 21h18M3 10h18M5 10v11M19 10v11M9 10v11M15 10v11M12 2 2 7h20L12 2Z"></path>
                </svg>
                <span>Enterprise Workspace</span>
                <span style="font-size: 10px; color: #a88094; margin-left: 2px;">▼</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_mid:
        st.markdown(
            """
            <div style="position: relative; display: flex; align-items: center; width: 100%; max-width: 520px; margin: 0 auto;">
                <div style="position: absolute; left: 14px; pointer-events: none; color: #a88094;">
                    <svg style="width: 15px; height: 15px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path>
                    </svg>
                </div>
                <input style="width: 100%; background: rgba(20, 6, 13, 0.7); border: 1px solid rgba(63, 23, 46, 0.9); border-radius: 16px; padding: 7px 48px 7px 38px; font-size: 12px; color: #ffffff; outline: none;" placeholder="Search or ask ENMA anything..." type="text" />
                <div style="position: absolute; right: 12px; display: flex; align-items: center;">
                    <span style="padding: 2px 6px; font-size: 10px; font-weight: 600; color: #a88094; background: #2b101f; border-radius: 4px; border: 1px solid #3f172e; font-family: monospace;">⌘K</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; justify-content: flex-end;">
                <div style="position: relative; padding: 6px; color: #a88094; border-radius: 12px; cursor: pointer;">
                    <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path>
                    </svg>
                    <span style="position: absolute; top: 4px; right: 4px; width: 8px; height: 8px; border-radius: 50%; background: #f43f76; box-shadow: 0 0 6px #f43f76;"></span>
                </div>
                <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #e11d5e 0%, #ff4d8d 100%); display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 11px; font-weight: 700; box-shadow: 0 0 8px rgba(244,63,118,0.4);">
                    HG
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

# Backward compatibility aliases
render_lucora_header = render_enma_header
render_aira_header = render_enma_header
