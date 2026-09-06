"""
Backwards compatibility shim for LUCORA Header.
Redirects to ENMA Header Component.
"""

from __future__ import annotations
from .enma_header import render_enma_header, render_lucora_header, render_aira_header

__all__ = ["render_enma_header", "render_lucora_header", "render_aira_header"]
