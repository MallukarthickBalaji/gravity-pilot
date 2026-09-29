"""
app.py — ASGI application entry point alias for GravityPilot backend.
Allows running: uvicorn backend.app:app
"""
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from api.server import app

__all__ = ["app"]
