"""
Clarification Component for Streamlit Application.
Renders missing parameter prompts when user instructions are incomplete or ambiguous.
"""

import streamlit as st
from schemas.task_schemas import TaskPlan

def render_clarification_card(plan: TaskPlan, on_resolve_callback, on_cancel_callback) -> None:
    """Renders an interactive card prompting the user for missing fields."""
    if not plan or not plan.clarification:
        return

    st.warning("⚠️ **Additional Information Required**")
    st.markdown(f"**Agent Inquiry:** *\"{plan.clarification.question_for_user}\"*")

    with st.form(key="clarification_form"):
        user_responses = {}
        for field in plan.clarification.missing_fields:
            clean_label = field.replace("_", " ").title()
            user_responses[field] = st.text_input(
                f"Please enter {clean_label}:",
                placeholder=f"e.g., recipient@university.edu" if "email" in field else f"Enter {clean_label}",
            )

        col_submit, col_cancel = st.columns([1, 1])
        with col_submit:
            submit = st.form_submit_button("✅ Submit Details & Resume", use_container_width=True)
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancel Task", use_container_width=True)

        if submit:
            if any(v.strip() for v in user_responses.values()):
                on_resolve_callback(user_responses)
            else:
                st.error("Please provide the requested information before submitting.")

        if cancel:
            on_cancel_callback()
