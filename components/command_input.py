"""
Command Console Component for Streamlit Application.
Provides natural language text input and quick-prompt chips.
"""

import streamlit as st

SAMPLE_PROMPTS = [
    ("📊 Project Update", "Send an email to dr.sharma@university.edu informing him that our BTech Major Project Phase 1 is complete and we would like to schedule a review on Friday at 3 PM."),
    ("❓ Missing Email (Clarification)", "Send an email to my project partner asking for the updated code repository link."),
    ("🚨 Urgent Outage", "Send an urgent email to ops@cloudservice.com stating that our database server is down with error 502 and requires immediate assistance."),
    ("📝 Formal Leave", "Send a formal leave application to director@institution.edu requesting absence on August 28th due to an academic symposium."),
]

def render_command_input(on_submit_callback) -> None:
    """Renders the conversational task console with quick-prompt chips."""
    st.markdown("### 📝 Command Console")
    st.caption("Enter your natural-language enterprise instruction below:")

    # Quick prompt chips
    st.markdown("**Quick Example Prompts:**")
    cols = st.columns(len(SAMPLE_PROMPTS))
    for idx, (label, prompt_text) in enumerate(SAMPLE_PROMPTS):
        with cols[idx]:
            if st.button(label, key=f"chip_{idx}", use_container_width=True):
                st.session_state["instruction_input"] = prompt_text
                st.rerun()

    # Main text input form
    default_text = st.session_state.get("instruction_input", "")
    with st.form(key="command_form", clear_on_submit=False):
        user_text = st.text_area(
            "Natural Language Instruction",
            value=default_text,
            height=90,
            placeholder="e.g., Send an email to advisor@university.edu informing them that our Phase 1 testing is complete...",
            label_visibility="collapsed",
        )
        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            submit = st.form_submit_button("🚀 Process Instruction", use_container_width=True)
        with col_info:
            st.caption("💡 *The AI agent will analyze intent, extract entities, and draft a verified execution plan.*")

        if submit and user_text.strip():
            on_submit_callback(user_text.strip())
