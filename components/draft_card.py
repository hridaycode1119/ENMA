"""
Human-in-the-Loop (HITL) Draft Review Card Component for Streamlit.
Allows users to review, edit in-place, and approve/cancel consequential actions.
"""

import streamlit as st
from schemas.task_schemas import EmailDraftPayload, EmailPriority, EmailTone, TaskPlan

def render_draft_card(
    plan: TaskPlan,
    on_approve_send,
    on_save_draft,
    on_cancel,
) -> None:
    """Renders an interactive, editable Human-in-the-Loop review card."""
    if not plan:
        return

    params = plan.tool_parameters
    recipient_email = params.get("recipient_email", "")
    recipient_name = params.get("recipient_name", "")
    subject = params.get("subject", "")
    body_text = params.get("body_text", "")
    current_tone = params.get("tone", "professional")
    current_priority = params.get("priority", "normal")

    st.markdown("### 👁️ Human-in-the-Loop (HITL) Review Gate")
    st.info("🔒 **Consequential Action Safety Gate Active:** Please verify the synthesized parameters below before execution.")

    tab_edit, tab_preview = st.tabs(["✏️ Edit Draft", "📄 Rendered HTML Preview"])

    with tab_edit:
        with st.form(key="hitl_draft_form"):
            col_to, col_name = st.columns([3, 2])
            with col_to:
                new_to = st.text_input("To (Recipient Email)*", value=recipient_email)
            with col_name:
                new_name = st.text_input("Recipient Name", value=recipient_name or "")

            new_subject = st.text_input("Subject Line*", value=subject)

            col_tone, col_priority = st.columns([1, 1])
            with col_tone:
                tone_options = ["formal", "professional", "urgent", "casual"]
                tone_idx = tone_options.index(current_tone) if current_tone in tone_options else 1
                new_tone = st.selectbox("Tone", tone_options, index=tone_idx)
            with col_priority:
                prio_options = ["low", "normal", "high"]
                prio_idx = prio_options.index(current_priority) if current_priority in prio_options else 1
                new_prio = st.selectbox("Priority", prio_options, index=prio_idx)

            new_body = st.text_area(
                "Email Body Message*",
                value=body_text,
                height=180,
            )

            st.divider()

            col_send, col_draft, col_cancel = st.columns([2, 2, 1])
            with col_send:
                approve_send = st.form_submit_button(
                    "🚀 Approve & Send Live",
                    type="primary",
                    use_container_width=True,
                )
            with col_draft:
                save_draft = st.form_submit_button(
                    "📝 Save as Gmail Draft",
                    use_container_width=True,
                )
            with col_cancel:
                cancel = st.form_submit_button(
                    "❌ Cancel",
                    use_container_width=True,
                )

            if approve_send:
                updated_payload = {
                    "recipient_email": new_to.strip(),
                    "recipient_name": new_name.strip() if new_name else None,
                    "subject": new_subject.strip(),
                    "body_text": new_body.strip(),
                    "tone": new_tone,
                    "priority": new_prio,
                }
                on_approve_send(updated_payload)

            if save_draft:
                updated_payload = {
                    "recipient_email": new_to.strip(),
                    "recipient_name": new_name.strip() if new_name else None,
                    "subject": new_subject.strip(),
                    "body_text": new_body.strip(),
                    "tone": new_tone,
                    "priority": new_prio,
                }
                on_save_draft(updated_payload)

            if cancel:
                on_cancel()

    with tab_preview:
        st.markdown(f"**From:** `Authenticated User`")
        st.markdown(f"**To:** `{new_to if 'new_to' in locals() else recipient_email}`")
        st.markdown(f"**Subject:** {new_subject if 'new_subject' in locals() else subject}")
        st.divider()
        preview_body = new_body if 'new_body' in locals() else body_text
        for p in preview_body.split("\n\n"):
            st.markdown(p.replace("\n", "<br>"), unsafe_allow_html=True)
