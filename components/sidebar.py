"""
Sidebar Component for Streamlit Application.
Displays Google OAuth status, registered tools, LLM settings, and execution history.
"""

import streamlit as st
from integrations.oauth_handler import GoogleOAuthHandler
from tools.registry import ToolRegistry
from tools.base import ToolSafetyLevel

def render_sidebar(oauth_handler: GoogleOAuthHandler, registry: ToolRegistry, orchestrator) -> None:
    """Renders the comprehensive sidebar navigation and settings panel."""
    with st.sidebar:
        st.markdown("### 🤖 Autonomous AI Agent")
        st.caption("Enterprise Task Automation Platform")
        st.divider()

        # 1. Google Workspace & OAuth Status
        st.markdown("#### 🔗 Workspace Integrations")
        is_auth = oauth_handler.is_authenticated()
        user_email = oauth_handler.get_authenticated_user_email()

        if is_auth:
            st.success(f"**Gmail API Active**\n`{user_email or 'user@workspace.com'}`")
        else:
            st.warning("⚠️ **Gmail API Disconnected**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔑 Connect", use_container_width=True, help="Launch Google OAuth browser login"):
                    import os
                    if os.path.exists(oauth_handler.credentials_file):
                        try:
                            oauth_handler.run_local_login_flow(port=8080)
                            st.success("Authenticated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Auth Error: {str(e)}")
                    else:
                        st.error("credentials.json not found in project root.")
            with col2:
                if st.button("🧪 Mock Auth", use_container_width=True, help="Use simulated offline account"):
                    oauth_handler.create_mock_authenticated_session("demo.user@enterprise.com")
                    st.rerun()

        st.divider()

        # 2. Registered Tool Capabilities
        st.markdown("#### 🛠️ Registered Tools")
        tools = registry.list_tools()
        for tool in tools:
            is_consequential = tool.safety_level == ToolSafetyLevel.CONSEQUENTIAL
            badge = "🔴 Consequential" if is_consequential else "🟢 Write-Safe"
            with st.expander(f"`{tool.name}`", expanded=False):
                st.caption(tool.description)
                st.markdown(f"**Safety Level:** {badge}")
                st.markdown(f"**Version:** `{tool.version}`")

        st.divider()

        # 3. AI Model Settings
        st.markdown("#### ⚙️ Cognitive Settings")
        selected_model = st.selectbox(
            "Reasoning Engine",
            ["gemini-1.5-flash", "gemini-1.5-pro", "mock-heuristic-core"],
            index=0,
            help="Select the inference model used for intent reasoning and draft synthesis."
        )
        temp = st.slider("Temperature (Creativity vs Determinism)", 0.0, 1.0, 0.2, 0.05)

        st.divider()

        # 4. Recent Task History
        st.markdown("#### 📜 Execution History")
        if orchestrator.history:
            for idx, item in enumerate(orchestrator.history[:5]):
                status_icon = "✅" if item["status"] == "COMPLETED" else "❌" if item["status"] == "FAILED" else "🚫"
                st.markdown(
                    f"{status_icon} **{item['intent'][:24]}...**  \n"
                    f"<small style='color: gray;'>Tool: {item['target_tool']} | ID: {item['task_id'][:8]}</small>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No past executions in current session.")

        st.divider()
        st.caption("👥 **Major Project Team:**\nVaishnavi Dhyani • Chetan • Hriday")
