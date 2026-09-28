"""
test_notebook.py — Verifies Jupyter notebook tool inspection and error handling.
"""
from __future__ import annotations

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from tools.notebook import op_open_notebook


def test_notebook_tool():
    print("=== Testing Notebook Tool ===")

    # 1. Non-existent file should raise FileNotFoundError
    try:
        op_open_notebook(source_path="non_existent_notebook_xyz.ipynb")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("  [OK] Missing notebook file correctly raised FileNotFoundError")

    # 2. Existing file: if Jupyter is absent, gracefully raise RuntimeError
    sample_nb = Path.home() / "Desktop" / "test_sample_check.ipynb"
    sample_nb.write_text('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}', encoding="utf-8")
    try:
        try:
            op_open_notebook(source_path=str(sample_nb))
            print("  [OK] Notebook launched or verified with installed Jupyter")
        except RuntimeError as exc:
            assert "Jupyter Notebook/Lab is not installed" in str(exc)
            print("  [OK] Absence of Jupyter correctly raised descriptive RuntimeError")
    finally:
        if sample_nb.exists():
            sample_nb.unlink()

    print("[SUCCESS] Notebook tool verified successfully!\n")


if __name__ == "__main__":
    test_notebook_tool()
