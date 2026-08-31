"""
Document Dynamic Tool Implementations for Agent Registry.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional

from modules.documents.converters import DocumentConverter
from modules.documents.editor import DocumentEditor
from tools.base import BaseTool, ToolMetadata, ToolResult, ToolSafetyLevel

class DocumentAnalyzeTool(BaseTool):
    """
    Analyzes document text, metadata, section breakdown, and word count.
    Classified as READ_ONLY.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="document_analyze_tool",
            display_name="Document Ingestion & Analyzer",
            description="Extracts sections, metadata, word statistics, and structure from documents.",
            safety_level=ToolSafetyLevel.READ_ONLY,
            version="1.0.0",
        )

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if "text" not in params and "raw_text" not in params:
            raise ValueError("Parameter 'text' or 'raw_text' is required.")
        return params

    def execute(self, validated_params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        text = validated_params.get("text") or validated_params.get("raw_text", "")
        filename = validated_params.get("filename", "document.txt")

        words = len(text.split())
        chars = len(text)
        lines = len(text.splitlines())

        data = {
            "filename": filename,
            "word_count": words,
            "char_count": chars,
            "line_count": lines,
            "preview": text[:200] + "..." if len(text) > 200 else text,
        }
        elapsed = (time.time() - start_time) * 1000
        return ToolResult(success=True, data=data, execution_time_ms=elapsed)

class DocumentEditTool(BaseTool):
    """
    Applies autonomous AI transformations or programmatic search-and-replace to documents.
    Classified as WRITE_SAFE.
    """

    def __init__(self, editor: Optional[DocumentEditor] = None):
        self.editor = editor or DocumentEditor()

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="document_edit_tool",
            display_name="AI Document Editor",
            description="Edits, summarizes, rewrites, or transforms document text according to instructions.",
            safety_level=ToolSafetyLevel.WRITE_SAFE,
            version="1.0.0",
        )

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if "text" not in params:
            raise ValueError("Parameter 'text' is required.")
        if "command" not in params and "find" not in params:
            raise ValueError("Either 'command' or 'find' parameter is required.")
        return params

    def execute(self, validated_params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        text = validated_params["text"]
        command = validated_params.get("command")
        tone = validated_params.get("tone", "professional")

        # Check for find and replace
        if "find" in validated_params:
            find_str = validated_params["find"]
            replace_str = validated_params.get("replace", "")
            new_text, count = self.editor.search_and_replace(text, find_str, replace_str)
            summary = f"Replaced {count} occurrences of '{find_str}'."
        else:
            new_text, summary = self.editor.execute_ai_command(text, command, tone=tone)

        elapsed = (time.time() - start_time) * 1000
        return ToolResult(
            success=True,
            data={"edited_text": new_text, "summary": summary, "original_length": len(text), "new_length": len(new_text)},
            execution_time_ms=elapsed,
        )

class DocumentConvertTool(BaseTool):
    """
    Converts document text into downloadable PDF, Word DOCX, Markdown, or TXT formats.
    Classified as WRITE_SAFE.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="document_convert_tool",
            display_name="Multi-Format Document Exporter",
            description="Converts text or markdown into styled PDF, Word DOCX, and Text binaries.",
            safety_level=ToolSafetyLevel.WRITE_SAFE,
            version="1.0.0",
        )

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if "text" not in params:
            raise ValueError("Parameter 'text' is required.")
        if "target_format" not in params:
            raise ValueError("Parameter 'target_format' is required (pdf, docx, md, txt).")
        return params

    def execute(self, validated_params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        text = validated_params["text"]
        fmt = validated_params["target_format"]
        title = validated_params.get("title", "Exported Document")

        try:
            converted_bytes = DocumentConverter.convert(text, target_format=fmt, title=title)
            elapsed = (time.time() - start_time) * 1000
            return ToolResult(
                success=True,
                data={
                    "format": fmt,
                    "byte_size": len(converted_bytes),
                    "title": title,
                },
                execution_time_ms=elapsed,
            )
        except Exception as ex:
            elapsed = (time.time() - start_time) * 1000
            return ToolResult(success=False, error_message=str(ex), execution_time_ms=elapsed)
