"""
Document Parsers Package and Unified Parser Factory.
"""

import os
from typing import Dict, Type
from .base import BaseDocumentParser, DocumentSection, ParsedDocument
from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from .tabular_parser import TabularParser
from .text_parser import TextParser

_PARSER_MAP: Dict[str, Type[BaseDocumentParser]] = {
    ".pdf": PDFParser,
    ".docx": DocxParser,
    ".doc": DocxParser,
    ".csv": TabularParser,
    ".xlsx": TabularParser,
    ".xls": TabularParser,
    ".txt": TextParser,
    ".md": TextParser,
    ".markdown": TextParser,
    ".json": TextParser,
    ".py": TextParser,
    ".log": TextParser,
}

class DocumentParserFactory:
    """Factory selecting the appropriate parser based on file extension."""

    @classmethod
    def get_parser(cls, filename: str) -> BaseDocumentParser:
        ext = os.path.splitext(filename)[1].lower()
        parser_cls = _PARSER_MAP.get(ext, TextParser)
        return parser_cls()

    @classmethod
    def parse(cls, file_bytes: bytes, filename: str) -> ParsedDocument:
        parser = cls.get_parser(filename)
        return parser.parse_bytes(file_bytes, filename=filename)

__all__ = [
    "BaseDocumentParser",
    "DocumentSection",
    "ParsedDocument",
    "PDFParser",
    "DocxParser",
    "TabularParser",
    "TextParser",
    "DocumentParserFactory",
]
