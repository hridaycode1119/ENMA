"""
ENMA Email Composer & Prebuilt Templates Component for Streamlit.
Provides clean fields for recipient emails, subject, custom body, prebuilt templates,
and instant on_click AI writing & polishing callbacks.
"""

from __future__ import annotations
import streamlit as st
from typing import Dict, Any, Optional

from integrations.resend_client import ResendClient
from tools.registry import ToolRegistry
from database.repository import ENMARepository, ENMARepository, AIRARepository
from modules.documents.editor import DocumentEditor

PREBUILT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "Meeting Request": {
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
            "ENMA Project Team"
        ),
    },
    "Leave Application": {
        "subject": "Leave Application: Request for Absence from [Start Date] to [End Date]",
        "body": (
            "Dear Team Lead,\n\n"
            "I am writing to formally request leave from [Start Date] to [End Date] due to personal commitments.\n\n"
            "During my absence:\n"
            "• Pending Tasks: All current milestone deliverables have been committed and documented.\n"
            "• Work Coverage: My team members have been briefed to handle urgent inquiries.\n"
            "• Availability: I will check emails periodically and remain reachable on phone for critical matters.\n\n"
            "Thank you for your consideration and approval.\n\n"
            "Best regards,\n"
            "[Your Name]"
        ),
    },
    "Project Status": {
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
    "BTech Major Project": {
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
    "Client Proposal": {
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
    "Urgent Alert": {
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
            "ENMA Monitoring System"
        ),
    },
    "Document Review": {
        "subject": "Document Review: System Architecture & Technical Specifications",
        "body": (
            "Hi Team,\n\n"
            "I have updated the system architecture and technical documentation for our AI automation platform.\n\n"
            "Please review the attached document sections regarding:\n"
            "1. Cognitive intent parser and Human-in-the-Loop approval workflows.\n"
            "2. Multi-format document parser specifications.\n"
            "3. Cloud database synchronization schema.\n\n"
            "Kindly submit your comments by tomorrow evening.\n\n"
            "Best regards,\n"
            "Engineering Lead"
        ),
    },
    "Weekly Sync Agenda": {
        "subject": "Agenda: Weekly Engineering Sprint Sync & Milestone Planning",
        "body": (
            "Dear Colleagues,\n\n"
            "Please find the proposed agenda for our upcoming weekly engineering sync:\n\n"
            "1. Sprint retrospectives and milestone achievements.\n"
            "2. Demonstration of autonomous Resend email dispatches.\n"
            "3. Multi-format document editor live benchmarking.\n"
            "4. Q&A and next action item assignments.\n\n"
            "Looking forward to our discussion.\n\n"
            "Best regards,\n"
            "Project Coordinator"
        ),
    },
}

def render_email_composer(
    key_prefix: str = "",
    on_email_sent_callback=None,
) -> None:
    """
    Renders an elegant, clean email composer with prebuilt templates,
    instant AI generation callbacks, and multi-provider dispatch.
    """
    repo = ENMARepository()
    resend_client = ResendClient()
    registry = ToolRegistry()
    editor = DocumentEditor()

    k_to = f"{key_prefix}email_to"
    k_subject = f"{key_prefix}email_subject"
    k_body = f"{key_prefix}email_body"
    k_provider = f"{key_prefix}email_provider"

    if k_to not in st.session_state:
        st.session_state[k_to] = ""
    if k_subject not in st.session_state:
        st.session_state[k_subject] = ""
    if k_body not in st.session_state:
        st.session_state[k_body] = ""

    # Instant on_click action callbacks
    def apply_template(tmpl_title: str):
        tmpl = PREBUILT_TEMPLATES.get(tmpl_title)
        if tmpl:
            st.session_state[k_subject] = tmpl["subject"]
            st.session_state[k_body] = tmpl["body"]

    def action_generate_full_email():
        current_text = st.session_state.get(k_body, "").strip()
        current_sub = st.session_state.get(k_subject, "").strip()
        to_email = st.session_state.get(k_to, "").strip()
        
        recipient_name = to_email.split("@")[0].capitalize() if to_email and "@" in to_email else "Team"
        prompt_input = current_text if current_text else (current_sub if current_sub else "project update and schedule sync")
        
        new_body = editor.generate_email_content(
            instruction=f"Write a comprehensive, professional email about: '{prompt_input}'.",
            recipient_name=recipient_name,
            tone="professional",
        )
        st.session_state[k_body] = new_body
        if not st.session_state.get(k_subject):
            st.session_state[k_subject] = f"Update regarding {prompt_input[:40].strip()}"

    def action_polish_executive():
        current_text = st.session_state.get(k_body, "").strip()
        if current_text:
            polished_text, _ = editor.execute_ai_command(
                document_text=current_text,
                instruction="Rewrite and polish this email in an authoritative, clear, and executive tone.",
                tone="professional",
            )
            st.session_state[k_body] = polished_text

    def action_make_concise():
        current_text = st.session_state.get(k_body, "").strip()
        if current_text:
            concise_text, _ = editor.execute_ai_command(
                document_text=current_text,
                instruction="Condense this email into a concise, direct, high-impact message with clear bullet points.",
                tone="concise",
            )
            st.session_state[k_body] = concise_text

    def action_fix_grammar():
        current_text = st.session_state.get(k_body, "").strip()
        if current_text:
            fixed_text, _ = editor.execute_ai_command(
                document_text=current_text,
                instruction="Fix all grammar, spelling, punctuation, and capitalization errors while preserving original intent.",
                tone="professional",
            )
            st.session_state[k_body] = fixed_text

    def action_clear_form():
        st.session_state[k_to] = ""
        st.session_state[k_subject] = ""
        st.session_state[k_body] = ""

    # 1. Prebuilt Templates Selection
    st.markdown("##### Select a Template")
    t_cols = st.columns(4)
    tmpl_list = list(PREBUILT_TEMPLATES.keys())
    for idx, tmpl_name in enumerate(tmpl_list):
        col_idx = idx % 4
        with t_cols[col_idx]:
            st.button(
                tmpl_name,
                key=f"{key_prefix}tmpl_btn_{idx}",
                use_container_width=True,
                on_click=apply_template,
                args=(tmpl_name,),
            )

    st.write("")

    # 2. Main Composer Interface (Tabs: Edit vs Preview)
    tab_compose, tab_preview = st.tabs(["Compose & AI Assistant", "Live HTML Preview"])

    with tab_compose:
        col_recipients, col_provider = st.columns([3, 1])
        with col_recipients:
            st.text_input(
                "Recipient Email Address(es)*",
                key=k_to,
                placeholder="e.g., hriday.code1119@gmail.com, chetan@enterprise.com",
            )
        with col_provider:
            default_prov = 0 if resend_client.is_configured() else 1
            st.selectbox(
                "Provider*",
                ["Resend Email API", "Gmail REST API"],
                index=default_prov,
                key=k_provider,
            )

        st.text_input(
            "Subject Line*",
            key=k_subject,
            placeholder="e.g., Meeting Request: Sprint Review & Architecture Sync",
        )

        # AI Generator Toolbar
        st.markdown("**Email Message Content:***")
        
        col_ai_btn, col_ai_hint = st.columns([2, 3])
        with col_ai_btn:
            st.button(
                "✦ Write Full Email with AI",
                key=f"{key_prefix}btn_ai_generate_full",
                type="secondary",
                use_container_width=True,
                on_click=action_generate_full_email,
            )

        with col_ai_hint:
            st.caption("Type rough notes below, then click to auto-expand into a polished email.")

        st.text_area(
            "Email Message Content",
            key=k_body,
            height=200,
            placeholder="Type your message or rough notes here (e.g., 'i want to schedule meeting with team tomorrow at 3pm')...",
            label_visibility="collapsed",
        )

        # AI Writing Tools Toolbar
        st.caption("Refine text with AI:")
        ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)
        with ai_col1:
            st.button(
                "Executive Polish",
                key=f"{key_prefix}btn_ai_polish",
                use_container_width=True,
                on_click=action_polish_executive,
            )

        with ai_col2:
            st.button(
                "Make Concise",
                key=f"{key_prefix}btn_ai_concise",
                use_container_width=True,
                on_click=action_make_concise,
            )

        with ai_col3:
            st.button(
                "Fix Grammar",
                key=f"{key_prefix}btn_ai_grammar",
                use_container_width=True,
                on_click=action_fix_grammar,
            )

        with ai_col4:
            st.button(
                "Clear Form",
                key=f"{key_prefix}btn_clear_composer",
                use_container_width=True,
                on_click=action_clear_form,
            )

        st.write("")

        # Send Action Buttons
        btn_send_col, btn_draft_col, _ = st.columns([2, 2, 3])
        with btn_send_col:
            send_btn = st.button("Send Email Live →", key=f"{key_prefix}btn_send_live", type="primary", use_container_width=True)
        with btn_draft_col:
            draft_btn = st.button("Save as Draft", key=f"{key_prefix}btn_save_draft", use_container_width=True)

        recipient_val = st.session_state.get(k_to, "").strip()
        subject_val = st.session_state.get(k_subject, "").strip()
        body_val = st.session_state.get(k_body, "").strip()
        selected_provider = st.session_state.get(k_provider, "Resend Email API")

        if send_btn:
            if not recipient_val:
                st.error("Please provide at least one recipient email address.")
            elif not subject_val:
                st.error("Please provide an email subject line.")
            elif not body_val:
                st.error("Please provide an email body message.")
            else:
                recipients = [r.strip() for r in recipient_val.split(",") if r.strip()]
                with st.spinner(f"Dispatching email via {selected_provider}..."):
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
                            st.success(f"**Email Dispatched Successfully!**\n• Message ID: `{tool_res.external_reference_id or 'sent-ok'}`\n• Provider: `{selected_provider}`\n• Recipients: `{', '.join(recipients)}`")
                            st.toast("Email delivered successfully", icon="✓")
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
            st.success("Draft saved to Notes successfully!")
            st.toast("Draft saved", icon="✓")

    with tab_preview:
        recipient_val = st.session_state.get(k_to, "")
        subject_val = st.session_state.get(k_subject, "")
        body_val = st.session_state.get(k_body, "")

        st.markdown(
            f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; background: #ffffff; color: #0f172a; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="border-bottom: 1px solid #f1f5f9; padding-bottom: 0.8rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.82rem; color: #64748b;"><strong>From:</strong> ENMA AI &lt;onboarding@resend.dev&gt;</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.2rem;"><strong>To:</strong> {recipient_val or '(No recipient specified)'}</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-top: 0.4rem;">{subject_val or '(No subject)'}</div>
                </div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #1e293b; white-space: pre-wrap;">
{body_val or '(Email body is empty)'}
                </div>
                <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 1.5rem 0 0.8rem 0;" />
                <div style="font-size: 0.75rem; color: #94a3b8; text-align: center;">
                    ✦ Sent autonomously via <strong>ENMA Enterprise AI Agent</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
