"""
notebook.py — Deterministic Jupyter notebook inspection and launcher tool.
Verifies notebook file existence and presence of jupyter environment before launching.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from tools.files import resolve_desktop_path

logger = logging.getLogger(__name__)


def op_open_notebook(source_path: str, dest_path: str = "", **_kwargs) -> dict[str, Any]:
    """Launch or verify a Jupyter notebook (.ipynb) file."""
    target = resolve_desktop_path(source_path)
    if not target.exists():
        cand = target.with_suffix(".ipynb")
        if cand.exists():
            target = cand
        else:
            raise FileNotFoundError(f"Notebook file not found: '{source_path}'")

    # Check if Jupyter Notebook or Jupyter Lab is available
    jupyter_bin = shutil.which("jupyter") or shutil.which("jupyter-notebook") or shutil.which("jupyter-lab")
    cmd = None
    if jupyter_bin:
        cmd = [jupyter_bin, "notebook", str(target)]
    else:
        try:
            chk = subprocess.run(
                [sys.executable, "-m", "notebook", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=4,
            )
            if chk.returncode == 0:
                cmd = [sys.executable, "-m", "notebook", str(target)]
        except Exception:
            pass

        if not cmd:
            try:
                chk = subprocess.run(
                    [sys.executable, "-m", "jupyterlab", "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=4,
                )
                if chk.returncode == 0:
                    cmd = [sys.executable, "-m", "jupyterlab", str(target)]
            except Exception:
                pass

    if not cmd:
        raise RuntimeError("Jupyter Notebook/Lab is not installed or is not available in PATH.")

    subprocess.Popen(cmd)
    return {
        "success": True,
        "source_path": str(target),
        "output_path": str(target),
        "operation": "open_notebook",
        "agent_type": "desktop_agent",
    }
