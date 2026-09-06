"""
Backwards compatibility shim for LUCORA Sidebar.
Redirects to ENMA Sidebar Component.
"""

from __future__ import annotations
from .enma_sidebar import render_enma_sidebar, render_lucora_sidebar, render_aira_sidebar

__all__ = ["render_enma_sidebar", "render_lucora_sidebar", "render_aira_sidebar"]
