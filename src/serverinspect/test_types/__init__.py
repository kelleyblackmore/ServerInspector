"""
DEPRECATED: Test type handlers for ServerInspect.

This module is deprecated. Use serverinspect.checkers instead.
"""

import logging
import importlib
import warnings

logger = logging.getLogger("serverinspect")

warnings.warn(
    "The test_types module is deprecated and will be removed in a future version. "
    "Use the checkers module instead.",
    DeprecationWarning,
    stacklevel=2,
)


def get_test_handler(test_type):
    """
    DEPRECATED: Get the handler for a specific test type.

    This function is deprecated. Use serverinspect.checkers.get_checker instead.

    Args:
        test_type (str): Type of test

    Returns:
        module: The test handler module

    Raises:
        ValueError: If the test type is not supported
    """
    warnings.warn(
        "get_test_handler is deprecated. Use serverinspect.checkers.get_checker instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        # Map test type to module
        test_type_map = {
            "file": "serverinspect.test_types.file",
            "directory": "serverinspect.test_types.file",  # Map directory type to file module
            "symlink": "serverinspect.test_types.file",  # Map symlink type to file module
            "service": "serverinspect.test_types.service",
            "process": "serverinspect.test_types.process",
            "command": "serverinspect.test_types.command",
            "package": "serverinspect.test_types.package",
            "port": "serverinspect.test_types.port",
        }

        if test_type not in test_type_map:
            raise ValueError(f"Unsupported test type: {test_type}")

        module_name = test_type_map[test_type]
        module = importlib.import_module(module_name)

        return module

    except ImportError as e:
        logger.error(f"Failed to import test handler for {test_type}: {str(e)}")
        raise ValueError(f"Test type '{test_type}' is not implemented") from e
