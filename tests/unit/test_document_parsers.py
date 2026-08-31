"""
Unit tests for Document Parsers (Text, Markdown, CSV, DOCX, PDF).
"""

import unittest
from modules.documents.parsers import DocumentParserFactory, TextParser, TabularParser, DocxParser, PDFParser

class TestDocumentParsers(unittest.TestCase):

    def test_text_parser(self):
        sample_text = "This is a sample document for autonomous task automation.\nSecond paragraph with details."
        parsed = DocumentParserFactory.parse(sample_text.encode("utf-8"), "test.txt")
        self.assertEqual(parsed.file_type, "txt")
        self.assertEqual(parsed.word_count, 13)
        self.assertEqual(len(parsed.sections), 1)

    def test_markdown_parser_sections(self):
        sample_md = "# Introduction\nWelcome to the project.\n\n# Architecture\nHexagonal design."
        parsed = DocumentParserFactory.parse(sample_md.encode("utf-8"), "README.md")
        self.assertEqual(parsed.file_type, "md")
        self.assertEqual(len(parsed.sections), 2)
        self.assertEqual(parsed.sections[0].title, "Introduction")
        self.assertEqual(parsed.sections[1].title, "Architecture")

    def test_csv_parser(self):
        sample_csv = "Task_ID,Assignee,Status\nTSK-01,Hriday,Done\nTSK-02,Chetan,In Progress\nTSK-03,Vaishnavi,Done\n"
        parsed = DocumentParserFactory.parse(sample_csv.encode("utf-8"), "tasks.csv")
        self.assertEqual(parsed.file_type, "csv")
        self.assertIn("Task_ID", parsed.metadata["columns"])
        self.assertEqual(parsed.metadata["row_count"], 3)
        self.assertEqual(parsed.sections[0].title, "CSV Data")

    def test_docx_roundtrip_parsing(self):
        from modules.documents.converters import DocumentConverter
        docx_bytes = DocumentConverter.text_to_docx("# Project Brief\nThis is a generated Word document.")
        parsed = DocumentParserFactory.parse(docx_bytes, "brief.docx")
        self.assertEqual(parsed.file_type, "docx")
        self.assertIn("Project Brief", parsed.raw_text)

    def test_pdf_roundtrip_parsing(self):
        from modules.documents.converters import DocumentConverter
        pdf_bytes = DocumentConverter.text_to_pdf("# Test PDF Title\nThis is a sample paragraph in PDF format.")
        parsed = DocumentParserFactory.parse(pdf_bytes, "test.pdf")
        self.assertEqual(parsed.file_type, "pdf")
        self.assertIn("Test PDF Title", parsed.raw_text)

if __name__ == "__main__":
    unittest.main()
