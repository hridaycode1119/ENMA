"""
PDF Document Parser using pypdf.
"""

from __future__ import annotations
import io
import os
from typing import Any, Dict, List

from .base import BaseDocumentParser, DocumentSection, ParsedDocument

class PDFParser(BaseDocumentParser):
    """Parses Adobe PDF (.pdf) documents."""

    def parse_bytes(self, file_bytes: bytes, filename: str = "document.pdf") -> ParsedDocument:
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            sections: List[DocumentSection] = []
            full_text_parts: List[str] = []

            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                full_text_parts.append(page_text)
                sections.append(
                    DocumentSection(
                        title=f"Page {idx + 1}",
                        content=page_text,
                        level=1,
                        page_number=idx + 1,
                    )
                )

            raw_text = "\n\n".join(full_text_parts)
            meta: Dict[str, Any] = {}
            if reader.metadata:
                meta = {
                    "title": reader.metadata.title or "",
                    "author": reader.metadata.author or "",
                    "creator": reader.metadata.creator or "",
                    "producer": reader.metadata.producer or "",
                }

            return ParsedDocument(
                filename=filename,
                file_type="pdf",
                raw_text=raw_text,
                sections=sections,
                metadata=meta,
                page_count=len(reader.pages) if len(reader.pages) > 0 else 1,
            )
        except Exception as ex:
            raise ValueError(f"Failed to parse PDF document '{filename}': {str(ex)}")

    def parse_file(self, file_path: str) -> ParsedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        with open(file_path, "rb") as f:
            return self.parse_bytes(f.read(), filename=os.path.basename(file_path))
