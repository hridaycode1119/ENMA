"""
Backwards compatibility shim for AIRA Dashboard.
Redirects to ENMA Master Enterprise Dashboard Component.
"""

from __future__ import annotations
from .enma_dashboard import render_enma_dashboard, render_lucora_dashboard, render_aira_dashboard

__all__ = ["render_enma_dashboard", "render_lucora_dashboard", "render_aira_dashboard"]
