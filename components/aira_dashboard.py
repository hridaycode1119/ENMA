"""
Backwards compatibility shim for AIRA Dashboard.
Redirects to LUCORA Master Enterprise Dashboard Component.
"""

from __future__ import annotations
from .lucora_dashboard import render_lucora_dashboard, render_aira_dashboard

__all__ = ["render_lucora_dashboard", "render_aira_dashboard"]
