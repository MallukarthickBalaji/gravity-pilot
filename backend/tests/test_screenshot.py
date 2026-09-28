"""
test_screenshot.py — Verifies screenshot capture tool.
"""
from __future__ import annotations

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from tools.screenshot import op_screenshot


def test_screenshot_tool():
    print("=== Testing Screenshot Tool ===")
    res = op_screenshot(dest_path="test_verify_screenshot.png")
    assert res.get("success") is True, f"Screenshot reported failure: {res.get('error')}"
    out_path = Path(res["output_path"])
    assert out_path.exists(), f"Screenshot file not found at: {out_path}"
    assert out_path.stat().st_size > 0, "Screenshot file is empty (0 bytes)"
    print(f"  [OK] Captured screenshot: {out_path.name} ({out_path.stat().st_size} bytes)")
    print("[SUCCESS] Screenshot tool verified successfully!\n")


if __name__ == "__main__":
    test_screenshot_tool()
