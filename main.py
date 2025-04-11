#!/usr/bin/env python3
"""
ServerInspect - A Python-based server inspection and testing tool.

Similar to InSpec, Goss, and ServerSpec, this tool allows you to define,
run, and report on server tests and audits.
"""

from serverinspect.cli import cli

if __name__ == '__main__':
    cli()
