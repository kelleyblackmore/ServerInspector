"""
ServerInspect system checkers.

This package provides simple functions to check various aspects of a system.
"""

import importlib
import logging

logger = logging.getLogger("serverinspect")


def get_checker(checker_type):
    """
    Get a checker function for the specified type.

    Args:
        checker_type (str): Type of checker to get

    Returns:
        function: Checker function
    """
    checker_map = {
        "file": "serverinspect.checkers.file",
        "command": "serverinspect.checkers.command",
        "service": "serverinspect.checkers.service",
        "process": "serverinspect.checkers.process",
        "package": "serverinspect.checkers.package",
        "port": "serverinspect.checkers.port",
    }

    if checker_type not in checker_map:
        raise ValueError(f"Unknown checker type: {checker_type}")

    try:
        module = importlib.import_module(checker_map[checker_type])
        return module.check
    except ImportError as e:
        logger.error(f"Failed to import checker for {checker_type}: {str(e)}")
        raise ValueError(f"Checker type '{checker_type}' is not available") from e
