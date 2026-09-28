"""
tools package — Deterministic action executors for DesktopPilot / GravityPilot.
"""
from tools.documents import (
    generate_code_file,
    generate_excel_sheet,
    generate_powerpoint,
    generate_word_doc,
    GENERATORS,
)
from tools.files import (
    is_protected_path,
    op_copy,
    op_create_file,
    op_create_folder,
    op_delete,
    op_launch_app,
    op_move,
    op_rename,
    resolve_desktop_path,
)
from tools.notebook import op_open_notebook
from tools.screenshot import op_screenshot
from tools.web_search import execute_multi_provider_search, open_url, web_search

__all__ = [
    "generate_word_doc",
    "generate_excel_sheet",
    "generate_powerpoint",
    "generate_code_file",
    "GENERATORS",
    "resolve_desktop_path",
    "is_protected_path",
    "op_create_file",
    "op_create_folder",
    "op_copy",
    "op_move",
    "op_rename",
    "op_delete",
    "op_launch_app",
    "op_screenshot",
    "op_open_notebook",
    "execute_multi_provider_search",
    "open_url",
    "web_search",
]
