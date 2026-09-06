"""
Universal Document Processing & AI File Studio Component for Streamlit.
Supports PDF, DOCX, CSV, XLSX, Markdown, and TXT editing, AI transformations, and multi-format exports.
"""

from __future__ import annotations
import difflib
import os
import streamlit as st

from modules.documents.parsers import DocumentParserFactory, ParsedDocument
from modules.documents.editor import DocumentEditor
from modules.documents.converters import DocumentConverter

QUICK_ACTIONS = [
    ("Executive Summary", "Generate a comprehensive executive summary with core takeaways and next steps."),
    ("Formal Polish", "Rewrite and polish this entire document in formal, professional enterprise prose."),
    ("Action Checklist", "Extract all key action items, tasks, and deliverables into a structured markdown checklist."),
    ("Formal English", "Translate and standardize any informal or multilingual sections into clear formal English."),
    ("Grammar Polish", "Fix all grammatical issues, standardize header capitalization, and polish punctuation."),
]

def render_document_studio() -> None:
    """Renders the comprehensive Document Processing and AI File Editing Studio."""
    st.markdown("### Document & Data Studio")
    st.caption("Upload and edit any PDF, Word (.docx), Excel (.xlsx), CSV, Markdown, or Text file with autonomous AI reasoning.")

    # Initialize studio session state
    if "doc_studio_parsed" not in st.session_state:
        st.session_state.doc_studio_parsed = None
    if "doc_studio_edited_text" not in st.session_state:
        st.session_state.doc_studio_edited_text = ""
    if "doc_studio_history" not in st.session_state:
        st.session_state.doc_studio_history = []
    if "doc_studio_editor" not in st.session_state:
        st.session_state.doc_studio_editor = DocumentEditor()

    editor: DocumentEditor = st.session_state.doc_studio_editor

    # 1. File Uploader Section
    col_upload, col_reset = st.columns([5, 1])
    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=["pdf", "docx", "doc", "txt", "md", "csv", "xlsx", "xls", "json", "py"],
            help="Upload any PDF, Word, Spreadsheet, or Text file to inspect and edit.",
            key="doc_file_uploader",
        )
    with col_reset:
        if st.session_state.doc_studio_parsed:
            st.write("")
            st.write("")
            if st.button("Clear File", use_container_width=True):
                st.session_state.doc_studio_parsed = None
                st.session_state.doc_studio_edited_text = ""
                st.rerun()

    # Process uploaded file
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name

        # Parse only if new file
        if not st.session_state.doc_studio_parsed or st.session_state.doc_studio_parsed.filename != filename:
            with st.spinner(f"Ingesting structured content from '{filename}'..."):
                try:
                    parsed = DocumentParserFactory.parse(file_bytes, filename)
                    st.session_state.doc_studio_parsed = parsed
                    st.session_state.doc_studio_edited_text = parsed.raw_text
                    st.toast(f"Parsed {filename} ({parsed.word_count} words)", icon="✓")
                except Exception as ex:
                    st.error(f"Failed to parse document: {str(ex)}")
                    return

    parsed: ParsedDocument = st.session_state.doc_studio_parsed

    if not parsed:
        st.info("✦ **Get Started:** Drag & drop any PDF, Word document, CSV/Excel file, or text document above to begin editing.")
        return

    # 2. Document Metrics Header
    st.divider()
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric("File Name", parsed.filename[:16] + "..." if len(parsed.filename) > 16 else parsed.filename)
    with m_col2:
        st.metric("Format", parsed.file_type.upper())
    with m_col3:
        st.metric("Word Count", f"{len(st.session_state.doc_studio_edited_text.split()):,}")
    with m_col4:
        st.metric("Est. Pages", max(1, len(st.session_state.doc_studio_edited_text.splitlines()) // 35))
    with m_col5:
        st.metric("Sections", len(parsed.sections))

    # 3. Autonomous AI Command Console
    st.markdown("#### AI Command Bar")
    st.caption("Select a quick-action or enter natural language instructions to edit the document:")

    # Quick Action Chips
    chip_cols = st.columns(len(QUICK_ACTIONS))
    for idx, (label, cmd_text) in enumerate(QUICK_ACTIONS):
        with chip_cols[idx]:
            if st.button(label, key=f"doc_chip_{idx}", use_container_width=True):
                with st.spinner(f"Executing: '{label}'..."):
                    new_text, summary = editor.execute_ai_command(
                        document_text=st.session_state.doc_studio_edited_text,
                        instruction=cmd_text,
                    )
                    st.session_state.doc_studio_edited_text = new_text
                    st.session_state.doc_studio_history.append((label, summary))
                    st.success(summary)
                    st.rerun()

    # Custom Command Form
    with st.form(key="doc_ai_command_form"):
        cmd_col, tone_col, btn_col = st.columns([5, 2, 2])
        with cmd_col:
            user_doc_cmd = st.text_input(
                "AI Edit Command",
                placeholder="e.g., 'Summarize section 2 and add a formal recommendation header at the end'",
                label_visibility="collapsed",
            )
        with tone_col:
            selected_tone = st.selectbox("Tone", ["professional", "academic", "concise", "formal", "casual"], index=0, label_visibility="collapsed")
        with btn_col:
            submit_cmd = st.form_submit_button("Execute AI Edit →", type="primary", use_container_width=True)

        if submit_cmd and user_doc_cmd.strip():
            with st.spinner(f"Executing: '{user_doc_cmd}'..."):
                new_text, summary = editor.execute_ai_command(
                    document_text=st.session_state.doc_studio_edited_text,
                    instruction=user_doc_cmd.strip(),
                    tone=selected_tone,
                )
                st.session_state.doc_studio_edited_text = new_text
                st.session_state.doc_studio_history.append((user_doc_cmd, summary))
                st.success(summary)
                st.rerun()

    # 4. Interactive Editor & Studio Tabs
    st.divider()
    tab_edit, tab_diff, tab_find_replace, tab_sections = st.tabs([
        "Live Document Editor",
        "Before / After Diff",
        "Find & Replace",
        "Section Appender",
    ])

    with tab_edit:
        st.caption("Directly edit document content in real-time below:")
        current_content = st.text_area(
            "Document Content",
            value=st.session_state.doc_studio_edited_text,
            height=320,
            key="doc_studio_live_textarea",
            label_visibility="collapsed",
        )
        if current_content != st.session_state.doc_studio_edited_text:
            st.session_state.doc_studio_edited_text = current_content

    with tab_diff:
        st.caption("Visual inspection of modifications compared to the original uploaded document:")
        orig_lines = parsed.raw_text.splitlines()
        edit_lines = st.session_state.doc_studio_edited_text.splitlines()
        diff = list(difflib.unified_diff(orig_lines, edit_lines, fromfile="Original", tofile="Edited", lineterm=""))

        if not diff:
            st.info("No modifications made yet. Original and current document are identical.")
        else:
            diff_text = "\n".join(diff[:150])
            st.code(diff_text, language="diff")

    with tab_find_replace:
        st.caption("Batch search and replace across the entire document buffer:")
        with st.form(key="find_replace_form"):
            f_col1, f_col2, f_col3 = st.columns([3, 3, 2])
            with f_col1:
                find_term = st.text_input("Find Text", placeholder="e.g., Old Client Name")
            with f_col2:
                replace_term = st.text_input("Replace With", placeholder="e.g., New Client Name")
            with f_col3:
                case_sens = st.checkbox("Case Sensitive", value=False)
                fr_submit = st.form_submit_button("Replace All →", use_container_width=True)

            if fr_submit and find_term:
                new_text, count = editor.search_and_replace(
                    st.session_state.doc_studio_edited_text,
                    find_str=find_term,
                    replace_str=replace_term,
                    case_sensitive=case_sens,
                )
                st.session_state.doc_studio_edited_text = new_text
                st.success(f"Successfully replaced {count} occurrence(s) of '{find_term}'.")
                st.rerun()

    with tab_sections:
        st.caption("Append or prepend titled sections (e.g. Conclusion, References, Executive Note):")
        with st.form(key="add_section_form"):
            sec_title = st.text_input("Section Title", placeholder="e.g., Executive Conclusion")
            sec_content = st.text_area("Section Content", placeholder="Enter section body text...", height=100)
            pos_col1, pos_col2 = st.columns(2)
            with pos_col1:
                add_append = st.form_submit_button("Append to End →", use_container_width=True)
            with pos_col2:
                add_prepend = st.form_submit_button("Prepend to Top →", use_container_width=True)

            if add_append and sec_title and sec_content:
                st.session_state.doc_studio_edited_text = editor.append_section(
                    st.session_state.doc_studio_edited_text, sec_title, sec_content
                )
                st.success(f"Appended section '{sec_title}'.")
                st.rerun()
            elif add_prepend and sec_title and sec_content:
                st.session_state.doc_studio_edited_text = editor.prepend_section(
                    st.session_state.doc_studio_edited_text, sec_title, sec_content
                )
                st.success(f"Prepended section '{sec_title}'.")
                st.rerun()

    # 5. Export & Download Center
    st.divider()
    st.markdown("#### Export & Download Center")
    st.caption("Export your edited document in any standard format with 1 click:")

    base_name = os.path.splitext(parsed.filename)[0]
    final_text = st.session_state.doc_studio_edited_text

    col_pdf, col_docx, col_md, col_txt = st.columns(4)

    # A. PDF Download
    with col_pdf:
        try:
            pdf_bytes = DocumentConverter.text_to_pdf(final_text, title=base_name.replace("_", " ").title())
            st.download_button(
                label="Download PDF →",
                data=pdf_bytes,
                file_name=f"{base_name}_edited.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception:
            st.button("PDF Unavailable", disabled=True, use_container_width=True)

    # B. Word DOCX Download
    with col_docx:
        try:
            docx_bytes = DocumentConverter.text_to_docx(final_text, title=base_name.replace("_", " ").title())
            st.download_button(
                label="Download Word (.docx) →",
                data=docx_bytes,
                file_name=f"{base_name}_edited.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception:
            st.button("DOCX Unavailable", disabled=True, use_container_width=True)

    # C. Markdown Download
    with col_md:
        st.download_button(
            label="Download Markdown →",
            data=final_text.encode("utf-8"),
            file_name=f"{base_name}_edited.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # D. Plain Text Download
    with col_txt:
        st.download_button(
            label="Download Text (.txt) →",
            data=final_text.encode("utf-8"),
            file_name=f"{base_name}_edited.txt",
            mime="text/plain",
            use_container_width=True,
        )
