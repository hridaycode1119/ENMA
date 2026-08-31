"""
Timeline & Execution Telemetry Component for Streamlit Application.
Renders real-time finite state machine progression and API response telemetry.
"""

import streamlit as st
from agent.orchestrator import WorkflowState

STEPS = [
    ("1. Ingest", [WorkflowState.PARSING, WorkflowState.CLARIFICATION_REQUIRED, WorkflowState.AWAITING_APPROVAL, WorkflowState.EXECUTING, WorkflowState.COMPLETED]),
    ("2. Plan & Reason", [WorkflowState.CLARIFICATION_REQUIRED, WorkflowState.AWAITING_APPROVAL, WorkflowState.EXECUTING, WorkflowState.COMPLETED]),
    ("3. HITL Review", [WorkflowState.AWAITING_APPROVAL, WorkflowState.EXECUTING, WorkflowState.COMPLETED]),
    ("4. API Execution", [WorkflowState.EXECUTING, WorkflowState.COMPLETED]),
    ("5. Verified Complete", [WorkflowState.COMPLETED]),
]

def render_timeline(state: WorkflowState, last_result, elapsed_ms: float = 0.0, on_reset_callback = None) -> None:
    """Renders the horizontal visual state progression and status badge."""
    st.markdown("### 📊 Workflow Execution Status")

    # Status Badge Row
    col_badge, col_time = st.columns([3, 1])
    with col_badge:
        if state == WorkflowState.IDLE:
            st.markdown("Status: `<span class='status-badge badge-idle'>⚪ IDLE - Ready for Task</span>`", unsafe_allow_html=True)
        elif state == WorkflowState.PARSING:
            st.markdown("Status: `<span class='status-badge badge-parsing'>⏳ PARSING - Reasoning over prompt...</span>`", unsafe_allow_html=True)
        elif state == WorkflowState.CLARIFICATION_REQUIRED:
            st.markdown("Status: `<span class='status-badge badge-clarification'>❓ CLARIFICATION - Awaiting Missing Info</span>`", unsafe_allow_html=True)
        elif state == WorkflowState.AWAITING_APPROVAL:
            st.markdown("Status: `<span class='status-badge badge-approval'>👁️ AWAITING APPROVAL - Review Draft</span>`", unsafe_allow_html=True)
        elif state == WorkflowState.EXECUTING:
            st.markdown("Status: `<span class='status-badge badge-executing'>⚡ EXECUTING - Communicating with Gmail API...</span>`", unsafe_allow_html=True)
        elif state == WorkflowState.COMPLETED:
            st.markdown("Status: `<span class='status-badge badge-completed'>✅ COMPLETED - Action Verified</span>`", unsafe_allow_html=True)
        elif state == WorkflowState.FAILED:
            st.markdown("Status: `<span class='status-badge badge-failed'>❌ FAILED - Action Aborted</span>`", unsafe_allow_html=True)
        elif state == WorkflowState.CANCELLED:
            st.markdown("Status: `<span class='status-badge badge-idle'>🚫 CANCELLED - Task Terminated</span>`", unsafe_allow_html=True)

    with col_time:
        if elapsed_ms > 0:
            st.caption(f"⏱️ Latency: **{elapsed_ms:.1f}ms**")

    # Step Progression Tracker
    cols = st.columns(len(STEPS))
    for idx, (label, active_in_states) in enumerate(STEPS):
        is_done = state in active_in_states
        is_current = (
            (idx == 0 and state == WorkflowState.PARSING)
            or (idx == 1 and state == WorkflowState.CLARIFICATION_REQUIRED)
            or (idx == 2 and state == WorkflowState.AWAITING_APPROVAL)
            or (idx == 3 and state == WorkflowState.EXECUTING)
            or (idx == 4 and state == WorkflowState.COMPLETED)
        )

        with cols[idx]:
            icon = "✅" if (is_done and not is_current) else ("⏳" if is_current else "⚪")
            border_style = "box-shadow: 0 0 10px rgba(79, 70, 229, 0.4);" if is_current else ""
            st.markdown(
                f"<div style='text-align: center; padding: 0.6rem 0.4rem; background: var(--neu-surface); border-radius: var(--radius-md); box-shadow: var(--neu-shadow-flat-sm); {border_style} font-size: 0.78rem; font-weight: {'700' if is_current else '500'};'>"
                f"{icon}<br>{label}</div>",
                unsafe_allow_html=True,
            )

    # If completed or failed, render outcome card
    if state == WorkflowState.COMPLETED and last_result:
        st.success(
            f"🎉 **Task Dispatched Successfully!**  \n"
            f"• **External Gmail Message ID:** `{last_result.external_reference_id}`  \n"
            f"• **Target Recipient:** `{last_result.data.get('recipient')}`  \n"
            f"• **Subject:** `{last_result.data.get('subject')}`"
        )
        if on_reset_callback:
            if st.button("➕ Start New Enterprise Task", type="primary"):
                on_reset_callback()

    elif state == WorkflowState.FAILED and last_result:
        st.error(f"❌ **Execution Failed:** {last_result.error_message}")
        if on_reset_callback:
            if st.button("🔄 Try Again"):
                on_reset_callback()
