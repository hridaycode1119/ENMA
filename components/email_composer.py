"""
AIRA Email Composer & Prebuilt Templates Component for Streamlit.
Provides dedicated fields for recipient emails, subject, custom body, prebuilt templates, and AI rewrites.
"""

from __future__ import annotations
import streamlit as st
from typing import Dict, Any, Optional

from integrations.resend_client import ResendClient
from tools.registry import ToolRegistry
from database.repository import AIRARepository
from modules.documents.editor import DocumentEditor

PREBUILT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "📊 Project Status Report": {
        "subject": "[Update] Project Status Report: Milestones Completed & Next Steps",
        "body": (
            "Hi Team,\n\n"
            "Here is our progress update for the current sprint:\n"
            "• Completed Milestones: AI Cognitive Core, Multi-Format Document Studio, and Cloud Database integration.\n"
            "• Verification: Automated test suites passing with 100% success rate.\n"
            "• Next Steps: Deployment validation and team review.\n\n"
            "Please let us know if you have any questions or feedback.\n\n"
            "Best regards,\n"
            "Project Team"
        ),
    },
    "📅 Meeting Invitation & Agenda": {
        "subject": "Meeting Request: Sprint Review & Planning Sync",
        "body": (
            "Dear Team,\n\n"
            "I would like to schedule a project sync meeting to discuss our upcoming deliverables.\n\n"
            "Proposed Agenda:\n"
            "1. Review of recent feature modules and integrations.\n"
            "2. Live demonstration of task execution pipelines.\n"
            "3. Q&A and next milestone scheduling.\n\n"
            "Please confirm if the proposed time slot works for you.\n\n"
            "Best regards,\n"
            "AIRA Project Team"
        ),
    },
    "🎓 Academic Major Project Progress": {
        "subject": "BTech Major Project: Bi-Weekly Progress Report Submission",
        "body": (
            "Respected Advisor,\n\n"
            "Please find below our progress summary for the Autonomous AI Agent for Enterprise Task Automation project:\n"
            "1. Team Members: Vaishnavi Dhyani, Chetan, Hriday.\n"
            "2. Key Implementations: Cognitive Reasoning Engine, Gmail & Resend API tool subsystem, and Supabase database persistence.\n"
            "3. Evaluation: 100% accuracy on cognitive reasoning benchmarks.\n\n"
            "We would be grateful for your review and guidance.\n\n"
            "Sincerely,\n"
            "Project Team"
        ),
    },
    "📄 Document Review & Feedback": {
        "subject": "Document Review: System Architecture & Technical Specifications",
        "body": (
            "Hello,\n\n"
            "Please review the updated technical documentation for our project.\n"
            "Kindly share your comments, suggestions, or approvals by the end of this week.\n\n"
            "Thank you for your time and assistance.\n\n"
            "Regards,\n"
            "Engineering Team"
        ),
    },
    "🚨 Urgent Action Required": {
        "subject": "URGENT: Action Required on Production Task Pipeline",
        "body": (
            "Hello,\n\n"
            "This is an automated high-priority alert regarding task pipeline execution.\n"
            "Please review the latest system telemetry and take necessary action immediately.\n\n"
            "Priority: High\n"
            "Status: Pending Review\n\n"
            "Thank you,\n"
            "AIRA Monitoring System"
        ),
    },
}

def render_email_composer(on_email_sent_callback=None) -> None:
    """Renders the comprehensive Email Composer with template selector and AI assistance."""
    st.markdown("### ✉️ Custom Email Composer & AI Studio")
    st.caption("Compose custom emails, load prebuilt enterprise templates, and dispatch via Resend or Gmail API.")

    resend_client = ResendClient()
    registry = ToolRegistry()
    repo = AIRARepository()
    doc_editor = DocumentEditor()

    # Session state initialization for composer
    if "composer_to" not in st.session_state:
        st.session_state.composer_to = ""
    if "composer_subject" not in st.session_state:
        st.session_state.composer_subject = ""
    if "composer_body" not in st.session_state:
        st.session_state.composer_body = ""

    # 1. Prebuilt Templates Quick Selection Bar
    st.markdown("#### 📋 Prebuilt Email Templates")
    st.caption("Click any template to auto-populate the subject and body:")

    t_cols = st.columns(len(PREBUILT_TEMPLATES))
    for idx, (tmpl_name, tmpl_data) in enumerate(PREBUILT_TEMPLATES.items()):
        with t_cols[idx]:
            if st.button(tmpl_name.split()[0] + " " + tmpl_name.split()[1], key=f"tmpl_btn_{idx}", use_container_width=True, help=tmpl_name):
                st.session_state.composer_subject = tmpl_data["subject"]
                st.session_state.composer_body = tmpl_data["body"]
                st.toast(f"Loaded template: {tmpl_name}", icon="📋")
                st.rerun()

    st.write("")

    # 2. Main Composer Interface (Tabs: Edit vs Preview)
    tab_compose, tab_preview = st.tabs(["✏️ Compose & Customize", "📄 Live HTML Preview"])

    with tab_compose:
        col_recipients, col_provider = st.columns([3, 1])
        with col_recipients:
            recipient_input = st.text_input(
                "Recipient Email Address(es)*",
                value=st.session_state.composer_to,
                placeholder="e.g., hriday.code1119@gmail.com, chetan@enterprise.com",
                help="Enter single email or comma-separated email addresses.",
                key="input_composer_to",
            )
        with col_provider:
            default_prov = 0 if resend_client.is_configured() else 1
            selected_provider = st.selectbox(
                "Dispatch Provider*",
                ["Resend Email API", "Gmail REST API"],
                index=default_prov,
                help="Choose email dispatch backend.",
            )

        subject_input = st.text_input(
            "Subject Line*",
            value=st.session_state.composer_subject,
            placeholder="e.g., [Update] Project Status Report: Milestones Completed",
            key="input_composer_subject",
        )

        body_input = st.text_area(
            "Custom Email Body Message*",
            value=st.session_state.composer_body,
            height=220,
            placeholder="Write your custom email message here or select a template above...",
            key="input_composer_body",
        )

        # AI Enhancement Buttons
        st.markdown("**🤖 AI Writing Assistant:**")
        ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)
        with ai_col1:
            if st.button("✨ Polish (Formal)", key="btn_ai_polish", use_container_width=True):
                if body_input.strip():
                    with st.spinner("Polishing draft with formal tone..."):
                        polished, _ = doc_editor.execute_ai_command(body_input, "Polish in formal executive prose")
                        st.session_state.composer_body = polished
                        st.rerun()
        with ai_col2:
            if st.button("✂️ Make Concise", key="btn_ai_concise", use_container_width=True):
                if body_input.strip():
                    with st.spinner("Summarizing into concise message..."):
                        concise, _ = doc_editor.execute_ai_command(body_input, "Rewrite concisely in bullet points")
                        st.session_state.composer_body = concise
                        st.rerun()
        with ai_col3:
            if st.button("🧹 Fix Grammar", key="btn_ai_grammar", use_container_width=True):
                if body_input.strip():
                    with st.spinner("Checking grammar and punctuation..."):
                        fixed, _ = doc_editor.execute_ai_command(body_input, "Fix all grammatical errors and polish punctuation")
                        st.session_state.composer_body = fixed
                        st.rerun()
        with ai_col4:
            if st.button("🗑️ Clear Form", key="btn_clear_composer", use_container_width=True):
                st.session_state.composer_to = ""
                st.session_state.composer_subject = ""
                st.session_state.composer_body = ""
                st.rerun()

        st.divider()

        # Send Action Buttons
        btn_send_col, btn_draft_col, _ = st.columns([2, 2, 3])
        with btn_send_col:
            send_btn = st.button("🚀 Send Email Live", type="primary", use_container_width=True)
        with btn_draft_col:
            draft_btn = st.button("💾 Save as Draft", use_container_width=True)

        if send_btn:
            if not recipient_input.strip():
                st.error("Please provide at least one recipient email address.")
            elif not subject_input.strip():
                st.error("Please provide an email subject line.")
            elif not body_input.strip():
                st.error("Please provide an email body message.")
            else:
                recipients = [r.strip() for r in recipient_input.split(",") if r.strip()]
                with st.spinner(f"🔒 Dispatching email via {selected_provider}..."):
                    try:
                        if "Resend" in selected_provider:
                            tool_res = registry.execute_tool(
                                tool_name="resend_send_tool",
                                parameters={
                                    "to": recipients if len(recipients) > 1 else recipients[0],
                                    "subject": subject_input.strip(),
                                    "body": body_input.strip(),
                                },
                                user_confirmed=True,
                            )
                        else:
                            tool_res = registry.execute_tool(
                                tool_name="gmail_send_tool",
                                parameters={
                                    "recipient_email": recipients[0],
                                    "subject": subject_input.strip(),
                                    "body_text": body_input.strip(),
                                },
                                user_confirmed=True,
                            )

                        if tool_res.success:
                            st.success(f"🎉 **Email Dispatched Successfully!**\n• Message ID: `{tool_res.external_reference_id or 'msg-success'}`\n• Provider: `{selected_provider}`\n• Recipients: `{', '.join(recipients)}`")
                            st.toast("Email delivered successfully", icon="✉️")
                            if on_email_sent_callback:
                                on_email_sent_callback(tool_res.data)
                        else:
                            st.error(f"Failed to dispatch: {tool_res.error_message}")
                    except Exception as ex:
                        st.error(f"Error during email delivery: {str(ex)}")

        if draft_btn and subject_input.strip():
            repo.save_note(
                title=f"Draft: {subject_input.strip()}",
                content=f"To: {recipient_input}\n\n{body_input}",
                category="note",
            )
            st.success("Draft saved to Notes and Database successfully!")
            st.toast("Draft saved", icon="💾")

    with tab_preview:
        st.markdown(
            f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; background: #ffffff; color: #1e293b; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                <div style="border-bottom: 1px solid #f1f5f9; padding-bottom: 0.8rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.82rem; color: #64748b;"><strong>From:</strong> AIRA AI &lt;onboarding@resend.dev&gt;</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.2rem;"><strong>To:</strong> {recipient_input or '(No recipient specified)'}</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-top: 0.4rem;">{subject_input or '(No subject)'}</div>
                </div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #334155; white-space: pre-wrap;">
{body_input or '(Email body is empty)'}
                </div>
                <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 1.5rem 0 0.8rem 0;" />
                <div style="font-size: 0.75rem; color: #94a3b8; text-align: center;">
                    ⚡ Sent autonomously via <strong>AIRA Enterprise AI Agent</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
