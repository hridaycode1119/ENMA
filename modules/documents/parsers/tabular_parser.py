"""
Tabular Document Parser for CSV and Excel (.xlsx) files.
"""

from __future__ import annotations
import io
import os
from typing import Any, Dict, List
import pandas as pd

from .base import BaseDocumentParser, DocumentSection, ParsedDocument

def _df_to_markdown(df: pd.DataFrame) -> str:
    """Converts DataFrame to Markdown table with pure Python fallback."""
    try:
        return df.head(50).to_markdown(index=False)
    except Exception:
        # Pure Python markdown table fallback
        headers = [str(c) for c in df.columns]
        header_row = "| " + " | ".join(headers) + " |"
        sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"
        rows = []
        for _, row in df.head(50).iterrows():
            rows.append("| " + " | ".join([str(val) for val in row.values]) + " |")
        return "\n".join([header_row, sep_row] + rows)

class TabularParser(BaseDocumentParser):
    """Parses tabular datasets (.csv, .xlsx)."""

    def parse_bytes(self, file_bytes: bytes, filename: str = "data.csv") -> ParsedDocument:
        try:
            ext = os.path.splitext(filename)[1].lower()
            sections: List[DocumentSection] = []
            tables_data: List[List[List[str]]] = []
            metadata: Dict[str, Any] = {}
            text_blocks: List[str] = []

            if ext in (".xlsx", ".xls"):
                excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    markdown_tbl = _df_to_markdown(df)
                    summary = f"### Sheet: {sheet_name}\n- **Rows:** {len(df)}\n- **Columns ({len(df.columns)}):** {', '.join(map(str, df.columns))}\n\n"
                    section_content = summary + markdown_tbl
                    text_blocks.append(section_content)
                    sections.append(
                        DocumentSection(title=f"Sheet: {sheet_name}", content=section_content)
                    )
                    # Table matrix
                    table_matrix = [list(map(str, df.columns))] + df.head(100).astype(str).values.tolist()
                    tables_data.append(table_matrix)
                metadata["sheet_names"] = excel_file.sheet_names
            else:
                # CSV
                df = pd.read_csv(io.BytesIO(file_bytes))
                markdown_tbl = _df_to_markdown(df)
                summary = f"### Dataset Overview\n- **Rows:** {len(df)}\n- **Columns ({len(df.columns)}):** {', '.join(map(str, df.columns))}\n\n"
                section_content = summary + markdown_tbl
                text_blocks.append(section_content)
                sections.append(DocumentSection(title="CSV Data", content=section_content))
                table_matrix = [list(map(str, df.columns))] + df.head(100).astype(str).values.tolist()
                tables_data.append(table_matrix)
                metadata["columns"] = list(df.columns)
                metadata["row_count"] = len(df)

            raw_text = "\n\n".join(text_blocks)

            return ParsedDocument(
                filename=filename,
                file_type="xlsx" if ext in (".xlsx", ".xls") else "csv",
                raw_text=raw_text,
                sections=sections,
                tables=tables_data,
                metadata=metadata,
                page_count=1,
            )
        except Exception as ex:
            raise ValueError(f"Failed to parse tabular document '{filename}': {str(ex)}")

    def parse_file(self, file_path: str) -> ParsedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tabular file not found: {file_path}")
        with open(file_path, "rb") as f:
            return self.parse_bytes(f.read(), filename=os.path.basename(file_path))
