#!/usr/bin/env python3
"""
serverinspector - A Python-based server inspection and testing tool.

Similar to InSpec, Goss, and ServerSpec, this tool allows you to define,
run, and report on server tests and audits.
"""

import sys
from pathlib import Path

from serverinspector.cli import cli

# Add the src directory to the Python path if it's not already there
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if __name__ == "__main__":
    cli()
