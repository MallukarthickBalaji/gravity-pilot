"""
main.py — Entry point for running the GravityPilot backend server.
"""
import os
import sys
from pathlib import Path

# Ensure backend directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from config import config

if __name__ == "__main__":
    port = int(os.environ.get("PORT", config.api_port))
    host = os.environ.get("HOST", config.api_host)
    print(f"Starting GravityPilot AI Backend on http://{host}:{port} ...")
    uvicorn.run("api.server:app", host=host, port=port, reload=False)
