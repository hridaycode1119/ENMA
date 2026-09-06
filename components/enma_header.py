"""
ENMA Top Header Bar Component.
Matches luxury burgundy / rose top bar layout with workspace selector, search with ⌘ K, bell and avatar.
"""

from __future__ import annotations
import streamlit as st

def render_enma_header(on_new_task_click=None) -> None:
    """Renders the luxury wine ENMA top header bar."""
    col_left, col_mid, col_right = st.columns([3, 6, 2])

    with col_left:
        st.markdown(
            """
            <div class="enma-workspace-pill">
                <span>🏛️</span>
                <span>Enterprise Workspace</span>
                <span style="font-size: 0.75rem; color: #fda4af;">▼</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_mid:
        st.markdown(
            """
            <div class="enma-search-bar">
                <div style="display: flex; align-items: center; gap: 0.6rem; width: 85%;">
                    <span style="color: #fda4af; font-size: 0.95rem;">🔍</span>
                    <input type="text" class="enma-search-input" placeholder="Search or ask ENMA anything..." />
                </div>
                <span class="enma-kbd-badge">⌘ K</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div class="enma-topbar-right" style="justify-content: flex-end;">
                <div class="enma-bell-btn">
                    <span>🔔</span>
                    <div class="enma-bell-dot"></div>
                </div>
                <div class="enma-user-avatar" style="width: 38px; height: 38px; font-size: 0.85rem;">
                    VD
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

# Backward-compatibility aliases
render_lucora_header = render_enma_header
render_aira_header = render_enma_header
