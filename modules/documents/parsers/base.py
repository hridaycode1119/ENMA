"""
Base Document Data Structures and Abstract Parser Interface.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

@dataclass
class DocumentSection:
    """Represents a structured section or chapter within a document."""
    title: str
    content: str
    level: int = 1
    page_number: Optional[int] = None

@dataclass
class ParsedDocument:
    """
    Universal representation of an ingested document across all supported file formats.
    """
    filename: str
    file_type: str                         # 'pdf', 'docx', 'csv', 'xlsx', 'txt', 'md'
    raw_text: str
    sections: List[DocumentSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    page_count: int = 1
    word_count: int = 0
    char_count: int = 0
    tables: List[List[List[str]]] = field(default_factory=list)
    parsed_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.word_count and self.raw_text:
            self.word_count = len(self.raw_text.split())
        if not self.char_count and self.raw_text:
            self.char_count = len(self.raw_text)

    def get_preview(self, max_chars: int = 500) -> str:
        """Returns a trimmed preview snippet of the document."""
        if len(self.raw_text) <= max_chars:
            return self.raw_text
        return self.raw_text[:max_chars].rstrip() + "\n... [Preview Truncated]"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "file_type": self.file_type,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "metadata": self.metadata,
            "section_count": len(self.sections),
            "table_count": len(self.tables),
        }

class BaseDocumentParser(ABC):
    """Abstract parser interface for extracting structured content from files."""

    @abstractmethod
    def parse_bytes(self, file_bytes: bytes, filename: str) -> ParsedDocument:
        """Parses in-memory raw file bytes into a ParsedDocument."""
        pass

    @abstractmethod
    def parse_file(self, file_path: str) -> ParsedDocument:
        """Parses a local filesystem file into a ParsedDocument."""
        pass
