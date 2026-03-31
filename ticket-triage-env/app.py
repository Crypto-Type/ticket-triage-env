# server/app.py
# Required entry point for OpenEnv multi-mode deployment spec

import uvicorn
import sys
import os

# Add parent directory to path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402


def main():
    """Server entry point — called by [project.scripts] in pyproject.toml"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
    )


if __name__ == "__main__":
    main()