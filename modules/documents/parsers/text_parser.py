"""
Plain Text, Markdown, and Code Document Parser.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List

from .base import BaseDocumentParser, DocumentSection, ParsedDocument

class TextParser(BaseDocumentParser):
    """Parses text, markdown, source code, and JSON files."""

    def parse_bytes(self, file_bytes: bytes, filename: str = "document.txt") -> ParsedDocument:
        try:
            # Try utf-8 decoding with fallback
            for encoding in ("utf-8", "latin-1", "cp1252"):
                try:
                    text = file_bytes.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = file_bytes.decode("utf-8", errors="replace")

            ext = os.path.splitext(filename)[1].lower().lstrip(".")
            if not ext:
                ext = "txt"

            sections: List[DocumentSection] = []
            if ext in ("md", "markdown"):
                # Split markdown by headings
                lines = text.splitlines()
                current_title = "Introduction"
                current_lines: List[str] = []
                for line in lines:
                    if line.startswith("#"):
                        if current_lines:
                            sections.append(DocumentSection(title=current_title, content="\n".join(current_lines)))
                            current_lines = []
                        current_title = line.lstrip("#").strip()
                    current_lines.append(line)
                if current_lines:
                    sections.append(DocumentSection(title=current_title, content="\n".join(current_lines)))
            else:
                sections.append(DocumentSection(title="Full Text", content=text))

            return ParsedDocument(
                filename=filename,
                file_type=ext,
                raw_text=text,
                sections=sections,
                metadata={"file_size_bytes": len(file_bytes), "line_count": len(text.splitlines())},
                page_count=max(1, len(text.splitlines()) // 40),
            )
        except Exception as ex:
            raise ValueError(f"Failed to parse text document '{filename}': {str(ex)}")

    def parse_file(self, file_path: str) -> ParsedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Text file not found: {file_path}")
        with open(file_path, "rb") as f:
            return self.parse_bytes(f.read(), filename=os.path.basename(file_path))
