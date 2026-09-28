"""
test_file_tools.py — Verifies deterministic filesystem tools.
Tests:
1. Create file and folder
2. Copy file
3. Move file
4. Rename file
5. Delete file
6. Protected system directory safety restrictions
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Ensure backend is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from tools.files import (
    is_protected_path,
    op_copy,
    op_create_file,
    op_create_folder,
    op_delete,
    op_move,
    op_rename,
    resolve_desktop_path,
)


def test_filesystem_operations():
    print("=== Testing Filesystem Operations ===")
    test_id = uuid.uuid4().hex[:6]
    test_dir_name = f"test_pilot_dir_{test_id}"
    desktop = Path.home() / "Desktop"

    # 1. Create Folder
    res_f = op_create_folder(source_path=test_dir_name)
    folder_path = Path(res_f["output_path"])
    assert folder_path.exists() and folder_path.is_dir(), f"Folder was not created: {folder_path}"
    print(f"  [OK] Created folder: {folder_path.name}")

    # 2. Create File
    file_name = f"{test_dir_name}/test_sample.txt"
    res_file = op_create_file(source_path=file_name, content="Hello DesktopPilot!")
    file_path = Path(res_file["output_path"])
    assert file_path.exists() and file_path.read_text(encoding="utf-8") == "Hello DesktopPilot!"
    print(f"  [OK] Created file: {file_path.name}")

    # 3. Copy File
    copy_name = f"{test_dir_name}/test_sample_copy.txt"
    res_copy = op_copy(source_path=str(file_path), dest_path=copy_name)
    copy_path = Path(res_copy["output_path"])
    assert copy_path.exists() and copy_path.read_text(encoding="utf-8") == "Hello DesktopPilot!"
    print(f"  [OK] Copied file to: {copy_path.name}")

    # 4. Rename File (bare filename)
    renamed_name = "test_sample_renamed.txt"
    res_rename = op_rename(source_path=str(copy_path), dest_path=renamed_name)
    renamed_path = Path(res_rename["output_path"])
    assert renamed_path.exists() and not copy_path.exists()
    print(f"  [OK] Renamed file to: {renamed_path.name}")

    # 5. Move File
    moved_name = f"{test_dir_name}/sub/test_sample_moved.txt"
    res_move = op_move(source_path=str(renamed_path), dest_path=moved_name)
    moved_path = Path(res_move["output_path"])
    assert moved_path.exists() and not renamed_path.exists()
    print(f"  [OK] Moved file to: {moved_path.name}")

    # 6. Delete File & Folder
    op_delete(source_path=str(file_path))
    assert not file_path.exists()
    op_delete(source_path=str(folder_path))
    assert not folder_path.exists()
    print("  [OK] Deleted test files and directory cleanly")

    # 7. Safety restriction check
    system_root = Path("C:\\Windows")
    assert is_protected_path(system_root), "SystemRoot must be protected!"
    try:
        op_delete(source_path="C:\\Windows")
        assert False, "Should have raised PermissionError on protected path!"
    except PermissionError:
        print("  [OK] Safety restriction blocked deletion of protected path")

    print("[SUCCESS] All filesystem tools verified successfully!\n")


if __name__ == "__main__":
    test_filesystem_operations()
