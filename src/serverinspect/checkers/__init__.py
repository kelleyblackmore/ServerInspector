"""
ServerInspect system checkers.

This package provides simple functions to check various aspects of a system.
"""

import importlib
import logging

logger = logging.getLogger("serverinspect")


def get_checker(checker_type):
    """
    Get a checker module for the specified type.

    Args:
        checker_type (str): Type of checker to get

    Returns:
        module: The checker module
    """
    checker_map = {
        "file": "serverinspect.checkers.file",
        "directory": "serverinspect.checkers.file",  # Map directory type to file module
        "symlink": "serverinspect.checkers.file",    # Map symlink type to file module
        "command": "serverinspect.checkers.command",
        "service": "serverinspect.checkers.service",
        "process": "serverinspect.checkers.process",
        "package": "serverinspect.checkers.package",
        "port": "serverinspect.checkers.port",
    }

    if checker_type not in checker_map:
        raise ValueError(f"Unknown checker type: {checker_type}")

    try:
        # Return the entire module, not just the check function
        module = importlib.import_module(checker_map[checker_type])
        return module
    except ImportError as e:
        logger.error(f"Failed to import checker for {checker_type}: {str(e)}")
        raise ValueError(f"Checker type '{checker_type}' is not available") from e
