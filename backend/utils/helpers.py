"""
helpers.py — Common helper utilities.
"""
from __future__ import annotations

import re
from pathlib import Path


def sanitize_filename(name: str, fallback: str = "output") -> str:
    """Sanitize string to be safe for filenames across operating systems."""
    if not name:
        return fallback
    clean = re.sub(r'[<>:"/\\|?*]', "_", name).strip()
    return clean or fallback


def format_byte_size(size_bytes: int) -> str:
    """Format bytes into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
