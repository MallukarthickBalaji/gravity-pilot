"""
screenshot.py — Deterministic desktop screenshot capture tool.
Captures primary or multi-screen display and saves to output directory or custom path.
"""
from __future__ import annotations

import ctypes
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import get_output_dir
from tools.files import resolve_desktop_path

logger = logging.getLogger(__name__)


def op_screenshot(source_path: str = "", dest_path: str = "", **_kwargs) -> dict[str, Any]:
    """Capture full desktop screen and save to PNG image."""
    from PIL import ImageGrab

    # Attach thread to interactive desktop if running in background thread
    try:
        u32 = ctypes.windll.user32
        hdesk = u32.OpenInputDesktop(0, False, 0x01FF)
        if hdesk:
            u32.SetThreadDesktop(hdesk)
    except Exception as dt_err:
        logger.debug("Desktop switch notice: %s", dt_err)

    target_name = dest_path or source_path
    if not target_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = get_output_dir() / f"screenshot_{timestamp}.png"
    else:
        target_path = resolve_desktop_path(target_name)
        if target_path.suffix.lower() != ".png":
            target_path = target_path.with_suffix(".png")

    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        img = ImageGrab.grab(all_screens=True)
        img.save(str(target_path), "PNG")
    except Exception:
        try:
            img = ImageGrab.grab()
            img.save(str(target_path), "PNG")
        except Exception as e:
            raise RuntimeError(f"Screenshot capture failed: {e}. Check screen permissions or lock state.")

    if not target_path.exists() or target_path.stat().st_size == 0:
        raise RuntimeError(f"Screenshot file was not saved or is 0 bytes: {target_path}")

    return {
        "success": True,
        "source_path": "",
        "output_path": str(target_path),
        "operation": "screenshot",
        "agent_type": "desktop_agent",
    }
