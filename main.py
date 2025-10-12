#!/usr/bin/env python3
"""
ServerInspect - Main entry point wrapper

This is a convenience entry point for development.
For production, use the executable or call src/main.py directly.
"""

# Import from the package in src
import sys
from pathlib import Path

# Add src to path if not already there
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import the CLI
from serverinspect.cli import cli  # noqa: E402

if __name__ == "__main__":
    cli()
