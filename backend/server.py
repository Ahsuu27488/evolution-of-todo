#!/usr/bin/env python3
"""Simple server runner for Chronos Todo API.

Usage:
    python server.py          # Run on default http://localhost:8000
    python server.py --port 8080    # Run on custom port
    python server.py --reload       # Enable auto-reload for development
"""

import sys
from pathlib import Path

# Add app directory to path so imports work
APP_DIR = Path(__file__).parent / "app"
sys.path.insert(0, str(APP_DIR.parent))

import uvicorn


def main():
    # Import app after path is set
    from app.main import app, logger

    # Parse simple command line args
    args = sys.argv[1:]
    host = "0.0.0.0"
    port = 8000
    reload = False

    for arg in args:
        if arg.startswith("--port="):
            port = int(arg.split("=")[1])
        elif arg == "--port" and len(args) > args.index(arg) + 1:
            port = int(args[args.index(arg) + 1])
        elif arg == "--reload":
            reload = True
        elif arg.startswith("--host="):
            host = arg.split("=")[1]

    logger.info(f"Starting Chronos Todo API on http://{host}:{port}")
    logger.info(f"Swagger UI: http://{host}:{port}/docs")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
