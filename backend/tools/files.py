"""
files.py — Deterministic filesystem operation tools.
Handles create, rename, move, copy, and delete for files and directories.
Protects against destructive actions on critical system folders.
"""
from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Critical system directories protected from modification or deletion
PROTECTED_PATHS = {
    Path(os.environ.get("SystemDrive", "C:") + "\\").resolve(),
    Path(os.environ.get("SystemRoot", "C:\\Windows")).resolve(),
    Path(os.environ.get("SystemRoot", "C:\\Windows") + "\\System32").resolve(),
    Path(os.environ.get("ProgramFiles", "C:\\Program Files")).resolve(),
    Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")).resolve(),
    Path.home().resolve(),
}


def is_protected_path(target: Path) -> bool:
    """Check if the given path is a protected system directory."""
    try:
        resolved = target.resolve()
        for p in PROTECTED_PATHS:
            if resolved == p:
                return True
        if resolved.parent == resolved:
            return True
    except Exception:
        pass
    return False


def resolve_desktop_path(path_str: str) -> Path:
    """
    Intelligently resolve friendly user paths (e.g. 'my desktop', 'Downloads', etc.)
    using dynamic Path.home().
    """
    if not path_str or not path_str.strip():
        return Path.home() / "Desktop"

    s = path_str.strip().strip("'\"")

    home = Path.home()
    desktop = home / "Desktop"
    downloads = home / "Downloads"
    documents = home / "Documents"
    pictures = home / "Pictures"

    s_lower = s.lower().replace("\\", "/")

    if s_lower in ("my desktop", "desktop", "desktop folder", "the desktop"):
        return desktop
    if s_lower in ("my downloads", "downloads", "downloads folder"):
        return downloads
    if s_lower in ("my documents", "documents", "documents folder"):
        return documents
    if s_lower in ("my pictures", "pictures", "pictures folder"):
        return pictures

    prefix_patterns = [
        (r"^(?:my\s+)?desktop(?:/|\\)?", desktop),
        (r"^(?:my\s+)?downloads(?:/|\\)?", downloads),
        (r"^(?:my\s+)?documents(?:/|\\)?", documents),
        (r"^(?:my\s+)?pictures(?:/|\\)?", pictures),
        (r"^~[/\\]?desktop(?:/|\\)?", desktop),
        (r"^~[/\\]?", home),
    ]

    for pattern, target_base in prefix_patterns:
        match = re.match(pattern, s, flags=re.IGNORECASE)
        if match:
            rest = s[match.end() :]
            return (target_base / rest).resolve()

    p = Path(s)
    if p.is_absolute():
        return p.resolve()

    desktop_candidate = (desktop / s).resolve()
    return desktop_candidate


def op_create_file(source_path: str, dest_path: str = "", content: str = "", **kwargs) -> dict[str, Any]:
    """Create a file with optional content."""
    target = resolve_desktop_path(source_path)
    if is_protected_path(target):
        raise PermissionError(f"Operation rejected: '{target}' is a protected system directory.")

    target.parent.mkdir(parents=True, exist_ok=True)
    file_content = content or kwargs.get("code") or kwargs.get("text") or ""
    if file_content:
        target.write_text(file_content, encoding="utf-8")
    elif not target.exists():
        target.touch()
    return {"success": True, "output_path": str(target), "operation": "create_file", "agent_type": "desktop_agent"}


def op_create_folder(source_path: str, dest_path: str = "", **_kwargs) -> dict[str, Any]:
    """Create a directory."""
    target = resolve_desktop_path(source_path)
    if is_protected_path(target):
        raise PermissionError(f"Operation rejected: '{target}' is a protected system directory.")

    target.mkdir(parents=True, exist_ok=True)
    return {"success": True, "output_path": str(target), "operation": "create_folder", "agent_type": "desktop_agent"}


def op_copy(source_path: str, dest_path: str, **_kwargs) -> dict[str, Any]:
    """Copy a file or directory to a destination."""
    src = resolve_desktop_path(source_path)
    dst = resolve_desktop_path(dest_path)

    if not src.exists():
        raise FileNotFoundError(f"Source path not found: '{src}'")

    if is_protected_path(dst):
        raise PermissionError(f"Operation rejected: Destination '{dst}' is a protected system directory.")

    if dst.is_dir() or not dst.suffix:
        dst.mkdir(parents=True, exist_ok=True)
        final_dst = dst / src.name
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        final_dst = dst

    if src.is_dir():
        shutil.copytree(str(src), str(final_dst), dirs_exist_ok=True)
    else:
        shutil.copy2(str(src), str(final_dst))

    return {
        "success": True,
        "source_path": str(src),
        "output_path": str(final_dst),
        "operation": "copy",
        "agent_type": "desktop_agent",
    }


def op_move(source_path: str, dest_path: str, **_kwargs) -> dict[str, Any]:
    """Move a file or directory to a new location."""
    src = resolve_desktop_path(source_path)
    dst = resolve_desktop_path(dest_path)

    if not src.exists():
        raise FileNotFoundError(f"Source path not found: '{src}'")

    if is_protected_path(src):
        raise PermissionError(f"Operation rejected: Source '{src}' is a protected system directory.")
    if is_protected_path(dst):
        raise PermissionError(f"Operation rejected: Destination '{dst}' is a protected system directory.")

    if dst.is_dir() or not dst.suffix:
        dst.mkdir(parents=True, exist_ok=True)
        final_dst = dst / src.name
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        final_dst = dst

    shutil.move(str(src), str(final_dst))
    return {
        "success": True,
        "source_path": str(src),
        "output_path": str(final_dst),
        "operation": "move",
        "agent_type": "desktop_agent",
    }


def op_rename(source_path: str, dest_path: str, **_kwargs) -> dict[str, Any]:
    """Rename a file or folder."""
    src = resolve_desktop_path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"Path not found to rename: '{src}'")

    if is_protected_path(src):
        raise PermissionError(f"Operation rejected: '{src}' is a protected system directory.")

    new_name = dest_path.strip().strip("'\"")
    if "/" not in new_name and "\\" not in new_name:
        final_dst = src.parent / new_name
    else:
        resolved_dst = resolve_desktop_path(new_name)
        final_dst = resolved_dst if resolved_dst.is_absolute() else src.parent / new_name

    final_dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(final_dst)
    return {
        "success": True,
        "source_path": str(src),
        "output_path": str(final_dst),
        "operation": "rename",
        "agent_type": "desktop_agent",
    }


def op_delete(source_path: str, dest_path: str = "", **_kwargs) -> dict[str, Any]:
    """Delete a file or directory."""
    target = resolve_desktop_path(source_path)
    if not target.exists():
        raise FileNotFoundError(f"Path not found: '{target}'")

    if is_protected_path(target):
        raise PermissionError(f"Safety restriction: Cannot delete protected directory '{target}'.")

    if target.is_dir():
        shutil.rmtree(str(target))
    else:
        target.unlink()

    return {
        "success": True,
        "source_path": str(target),
        "output_path": str(target),
        "operation": "delete",
        "agent_type": "desktop_agent",
    }


def op_launch_app(source_path: str, dest_path: str = "", **_kwargs) -> dict[str, Any]:
    """Launch a desktop application executable."""
    app_target = source_path.strip()
    subprocess.Popen(app_target, shell=True)
    return {
        "success": True,
        "source_path": app_target,
        "output_path": app_target,
        "operation": "launch_app",
        "agent_type": "desktop_agent",
    }
