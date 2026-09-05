"""
AIRA Email Composer & Prebuilt Templates Component for Streamlit.
Provides dedicated fields for recipient emails, subject, custom body, prebuilt templates, and AI generation.
"""

from __future__ import annotations
import streamlit as st
from typing import Dict, Any, Optional

from integrations.resend_client import ResendClient
from tools.registry import ToolRegistry
from database.repository import AIRARepository
from modules.documents.editor import DocumentEditor

PREBUILT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "📅 Meeting Request": {
        "subject": "Meeting Request: Sprint Review & Architecture Sync",
        "body": (
            "Dear Team,\n\n"
            "I would like to schedule a project sync meeting to discuss our upcoming deliverables.\n\n"
            "Proposed Agenda:\n"
            "1. Review of recent feature modules and integrations.\n"
            "2. Live demonstration of task execution pipelines.\n"
            "3. Q&A, blockers resolution, and next milestone scheduling.\n\n"
            "Proposed Time: Tomorrow at 3:00 PM IST (Google Meet)\n\n"
            "Please let me know if this time works for you.\n\n"
            "Best regards,\n"
            "AIRA Project Team"
        ),
    },
    "🏖️ Holiday / Leave": {
        "subject": "Leave Application: Request for Absence from [Start Date] to [End Date]",
        "body": (
            "Dear [Manager / Team Lead],\n\n"
            "I am writing to formally request leave from [Start Date] to [End Date] due to [personal reasons / medical emergency / family vacation].\n\n"
            "During my absence:\n"
            "• Pending Tasks: All current milestone deliverables have been committed and documented.\n"
            "• Work Coverage: My team members have been briefed to handle urgent inquiries.\n"
            "• Availability: I will check emails periodically and remain reachable on phone for critical matters.\n\n"
            "Thank you for your consideration and approval.\n\n"
            "Best regards,\n"
            "[Your Name]"
        ),
    },
    "📊 Project Progress": {
        "subject": "[Update] Project Status Report: Milestones Completed & Next Steps",
        "body": (
            "Hi Team,\n\n"
            "Here is our progress update for the current sprint:\n"
            "• Completed Milestones: AI Cognitive Core, Multi-Format Document Studio, and Cloud Database integration.\n"
            "• Quality Assurance: All automated test suites passing with 100% test coverage.\n"
            "• Next Steps: Deployment validation, security checks, and user feedback collection.\n\n"
            "Please feel free to share any feedback or questions.\n\n"
            "Best regards,\n"
            "Project Automation Team"
        ),
    },
    "🎓 BTech Major Project": {
        "subject": "BTech Major Project: Bi-Weekly Progress Report Submission",
        "body": (
            "Respected Advisor / Project Coordinator,\n\n"
            "Please find below our progress summary for the Autonomous AI Agent for Enterprise Task Automation project:\n"
            "1. Team Members: Vaishnavi Dhyani, Chetan, Hriday.\n"
            "2. Key Implementations: Cognitive Reasoning Engine, Gmail & Resend API tool subsystem, Universal Document Studio, and Supabase database persistence.\n"
            "3. Evaluation: 100% accuracy on cognitive reasoning benchmark tests.\n\n"
            "We would be grateful for your review and suggestions.\n\n"
            "Sincerely,\n"
            "Project Team"
        ),
    },
    "💼 Client Proposal": {
        "subject": "Partnership Proposal: Autonomous Task Automation Solutions for Enterprise",
        "body": (
            "Dear [Client Name],\n\n"
            "Thank you for your interest in our enterprise automation solutions.\n\n"
            "Our autonomous AI agent platform streamlines enterprise workflows by:\n"
            "• Automating multi-format document processing (PDF, DOCX, XLSX).\n"
            "• Executing verified email dispatches with Human-in-the-Loop safety gates.\n"
            "• Integrating calendar scheduling and cloud database persistence.\n\n"
            "We would love to demonstrate a 15-minute live demo this week. Please let us know your availability.\n\n"
            "Best regards,\n"
            "Business Development Team"
        ),
    },
    "🚨 Urgent Escalation": {
        "subject": "URGENT: Production Alert & Immediate Action Required",
        "body": (
            "Hello Team,\n\n"
            "This is an automated high-priority alert regarding task pipeline execution.\n"
            "Please review the system logs immediately to prevent workflow disruption.\n\n"
            "Incident Details:\n"
            "• Severity: High\n"
            "• Affected Component: Enterprise Task Worker\n"
            "• Action Required: Please verify credentials and restore worker process.\n\n"
            "Thank you,\n"
            "AIRA Monitoring System"
        ),
    },
    "📝 Document Review": {
        "subject": "Document Review: System Architecture & Technical Specifications",
        "body": (
            "Hello,\n\n"
            "Please review the updated technical documentation for our project.\n"
            "Kindly share your comments, suggestions, or approvals by the end of this week.\n\n"
            "Key Sections for Review:\n"
            "1. Architectural DFD & Class Diagrams\n"
            "2. Security & Zero-Bypass Action Guard\n"
            "3. Database Persistence Layer\n\n"
            "Thank you for your time and assistance.\n\n"
            "Regards,\n"
            "Engineering Team"
        ),
    },
    "💰 Payment Reminder": {
        "subject": "Invoice Follow-Up: Milestone Completion & Payment Processing",
        "body": (
            "Dear Accounts Team,\n\n"
            "I hope this email finds you well.\n\n"
            "This is a gentle reminder regarding Invoice #[Invoice Number] for completed project milestones, which was submitted on [Date].\n\n"
            "Please let us know if you require any additional documents or approvals to process the payment.\n\n"
            "Thank you for your prompt assistance.\n\n"
            "Best regards,\n"
            "Finance & Operations Team"
        ),
    },
}

def render_email_composer(on_email_sent_callback=None, default_to: str = "") -> None:
    """Renders the comprehensive Email Composer with template selector and working AI assistance."""
    st.markdown("### ✉️ Custom Email Composer & AI Studio")
    st.caption("Compose custom emails, load prebuilt enterprise templates, or let AI generate the full content.")

    resend_client = ResendClient()
    registry = ToolRegistry()
    repo = AIRARepository()
    doc_editor = DocumentEditor()

    # Initialize session state keys for the widgets
    if "input_composer_to" not in st.session_state:
        st.session_state.input_composer_to = default_to or "hriday.code1119@gmail.com"
    if "input_composer_subject" not in st.session_state:
        st.session_state.input_composer_subject = ""
    if "input_composer_body" not in st.session_state:
        st.session_state.input_composer_body = ""

    # 1. Prebuilt Templates Quick Selection Bar
    st.markdown("#### 📋 Prebuilt Enterprise Templates")
    st.caption("Click any template to auto-populate the subject and body:")

    t_cols = st.columns(4)
    for idx, (tmpl_name, tmpl_data) in enumerate(PREBUILT_TEMPLATES.items()):
        col_idx = idx % 4
        with t_cols[col_idx]:
            if st.button(tmpl_name, key=f"tmpl_btn_{idx}", use_container_width=True):
                st.session_state["input_composer_subject"] = tmpl_data["subject"]
                st.session_state["input_composer_body"] = tmpl_data["body"]
                st.toast(f"Loaded: {tmpl_name}", icon="📋")
                st.rerun()

    st.write("")

    # 2. Main Composer Interface (Tabs: Edit vs Preview)
    tab_compose, tab_preview = st.tabs(["✏️ Compose & AI Assistant", "📄 Live HTML Preview"])

    with tab_compose:
        col_recipients, col_provider = st.columns([3, 1])
        with col_recipients:
            st.text_input(
                "Recipient Email Address(es)*",
                key="input_composer_to",
                placeholder="e.g., hriday.code1119@gmail.com, chetan@enterprise.com",
                help="Enter single email or comma-separated email addresses.",
            )
        with col_provider:
            default_prov = 0 if resend_client.is_configured() else 1
            selected_provider = st.selectbox(
                "Dispatch Provider*",
                ["Resend Email API", "Gmail REST API"],
                index=default_prov,
                help="Choose email dispatch backend.",
                key="input_composer_provider",
            )

        st.text_input(
            "Subject Line*",
            key="input_composer_subject",
            placeholder="e.g., Meeting Request: Sprint Review & Architecture Sync",
        )

        # AI Generator Banner & Button right above the body box
        st.markdown("**Custom Email Body Message:***")
        
        col_ai_btn, col_ai_hint = st.columns([2, 3])
        with col_ai_btn:
            if st.button("🤖 ✨ Write / Generate Full Email with AI", type="secondary", use_container_width=True):
                current_text = st.session_state.get("input_composer_body", "").strip()
                current_subj = st.session_state.get("input_composer_subject", "").strip()
                prompt_input = current_text if current_text else current_subj
                
                if not prompt_input:
                    prompt_input = "Write a professional project progress update email to team"

                with st.spinner("🤖 AIRA AI generating full professional email..."):
                    try:
                        instruction = (
                            f"Write a complete, professional, beautifully structured enterprise email based on this input: '{prompt_input}'. "
                            "Include an appropriate greeting, clearly written paragraphs with bullet points for key details, and a professional sign-off. "
                            "Do not include meta-text or explanation."
                        )
                        generated_body, _ = doc_editor.execute_ai_command(
                            document_text=current_text or prompt_input,
                            instruction=instruction,
                            tone="professional",
                        )
                        st.session_state["input_composer_body"] = generated_body
                        
                        if not current_subj:
                            st.session_state["input_composer_subject"] = f"[Update] {prompt_input.split('.')[0][:50]}"
                            
                        st.toast("Full email generated with AI!", icon="✨")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"AI Generation Error: {str(ex)}")

        with col_ai_hint:
            st.caption("💡 *Type rough notes or instructions in the box below, then click the AI button above to expand into a complete email!*")

        st.text_area(
            "Email Message Content",
            key="input_composer_body",
            height=240,
            placeholder="Type your message or rough notes here (e.g., 'Tell Chetan that Phase 5 is finished and schedule demo tomorrow at 4pm')...",
            label_visibility="collapsed",
        )

        # AI Transformation Action Toolbar
        st.markdown("**✨ AI Writing & Editing Tools:**")
        ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)
        with ai_col1:
            if st.button("👔 Polish (Executive)", key="btn_ai_polish", use_container_width=True):
                curr = st.session_state.get("input_composer_body", "")
                if curr.strip():
                    with st.spinner("Polishing tone..."):
                        polished, _ = doc_editor.execute_ai_command(curr, "Rewrite in a formal, highly articulate executive tone")
                        st.session_state["input_composer_body"] = polished
                        st.toast("Draft polished in executive tone!", icon="👔")
                        st.rerun()
                else:
                    st.warning("Please type some email content first.")

        with ai_col2:
            if st.button("✂️ Make Concise", key="btn_ai_concise", use_container_width=True):
                curr = st.session_state.get("input_composer_body", "")
                if curr.strip():
                    with st.spinner("Condensing content..."):
                        concise, _ = doc_editor.execute_ai_command(curr, "Rewrite into concise bullet points and direct action items")
                        st.session_state["input_composer_body"] = concise
                        st.toast("Draft condensed into concise points!", icon="✂️")
                        st.rerun()
                else:
                    st.warning("Please type some email content first.")

        with ai_col3:
            if st.button("🧹 Fix Grammar", key="btn_ai_grammar", use_container_width=True):
                curr = st.session_state.get("input_composer_body", "")
                if curr.strip():
                    with st.spinner("Fixing grammar..."):
                        fixed, _ = doc_editor.execute_ai_command(curr, "Fix all spelling, punctuation, and grammatical mistakes while retaining original meaning")
                        st.session_state["input_composer_body"] = fixed
                        st.toast("Grammar and punctuation polished!", icon="🧹")
                        st.rerun()
                else:
                    st.warning("Please type some email content first.")

        with ai_col4:
            if st.button("🗑️ Clear Form", key="btn_clear_composer", use_container_width=True):
                st.session_state["input_composer_to"] = ""
                st.session_state["input_composer_subject"] = ""
                st.session_state["input_composer_body"] = ""
                st.toast("Form cleared", icon="🗑️")
                st.rerun()

        st.divider()

        # Send Action Buttons
        btn_send_col, btn_draft_col, _ = st.columns([2, 2, 3])
        with btn_send_col:
            send_btn = st.button("🚀 Send Email Live", type="primary", use_container_width=True)
        with btn_draft_col:
            draft_btn = st.button("💾 Save as Draft", use_container_width=True)

        recipient_val = st.session_state.get("input_composer_to", "").strip()
        subject_val = st.session_state.get("input_composer_subject", "").strip()
        body_val = st.session_state.get("input_composer_body", "").strip()

        if send_btn:
            if not recipient_val:
                st.error("Please provide at least one recipient email address.")
            elif not subject_val:
                st.error("Please provide an email subject line.")
            elif not body_val:
                st.error("Please provide an email body message.")
            else:
                recipients = [r.strip() for r in recipient_val.split(",") if r.strip()]
                with st.spinner(f"🔒 Dispatching email via {selected_provider}..."):
                    try:
                        if "Resend" in selected_provider:
                            tool_res = registry.execute_tool(
                                tool_name="resend_send_tool",
                                parameters={
                                    "to": recipients if len(recipients) > 1 else recipients[0],
                                    "subject": subject_val,
                                    "body": body_val,
                                },
                                user_confirmed=True,
                            )
                        else:
                            tool_res = registry.execute_tool(
                                tool_name="gmail_send_tool",
                                parameters={
                                    "recipient_email": recipients[0],
                                    "subject": subject_val,
                                    "body_text": body_val,
                                },
                                user_confirmed=True,
                            )

                        if tool_res.success:
                            st.success(f"🎉 **Email Dispatched Successfully!**\n• Message ID: `{tool_res.external_reference_id or 'sent-ok'}`\n• Provider: `{selected_provider}`\n• Recipients: `{', '.join(recipients)}`")
                            st.toast("Email delivered successfully", icon="✉️")
                            if on_email_sent_callback:
                                on_email_sent_callback(tool_res.data)
                        else:
                            st.error(f"Failed to dispatch: {tool_res.error_message}")
                    except Exception as ex:
                        st.error(f"Error during email delivery: {str(ex)}")

        if draft_btn and subject_val:
            repo.save_note(
                title=f"Draft: {subject_val}",
                content=f"To: {recipient_val}\n\n{body_val}",
                category="note",
            )
            st.success("Draft saved to Notes and Database successfully!")
            st.toast("Draft saved", icon="💾")

    with tab_preview:
        recipient_val = st.session_state.get("input_composer_to", "")
        subject_val = st.session_state.get("input_composer_subject", "")
        body_val = st.session_state.get("input_composer_body", "")

        st.markdown(
            f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; background: #ffffff; color: #0f172a; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                <div style="border-bottom: 1px solid #f1f5f9; padding-bottom: 0.8rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.82rem; color: #64748b;"><strong>From:</strong> AIRA AI &lt;onboarding@resend.dev&gt;</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.2rem;"><strong>To:</strong> {recipient_val or '(No recipient specified)'}</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-top: 0.4rem;">{subject_val or '(No subject)'}</div>
                </div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #1e293b; white-space: pre-wrap;">
{body_val or '(Email body is empty)'}
                </div>
                <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 1.5rem 0 0.8rem 0;" />
                <div style="font-size: 0.75rem; color: #94a3b8; text-align: center;">
                    ⚡ Sent autonomously via <strong>AIRA Enterprise AI Agent</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
