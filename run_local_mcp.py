"""Standalone entrypoint to run the Abhishek Second Brain MCP Server over stdio.

Usage in Claude Desktop / MCP Clients:
    python run_local_mcp.py
"""

import os
import sys
from pathlib import Path

# Ensure UTF-8 encoding on Windows stdio pipes
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add mcp folder to sys.path
root_dir = Path(__file__).resolve().parent
mcp_dir = root_dir / "mcp"
sys.path.insert(0, str(mcp_dir))
sys.path.insert(0, str(root_dir))

# Default workspace to root directory
if len(sys.argv) == 1:
    sys.argv.append(str(root_dir))

from local_server import main

if __name__ == "__main__":
    main()
