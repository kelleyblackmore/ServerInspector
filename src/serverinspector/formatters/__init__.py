"""
Output formatters for serverinspector.
"""

import logging

logger = logging.getLogger("serverinspector")


def get_formatter(format_name):
    """
    Get the formatter for the specified format.

    Args:
        format_name (str): Name of the format

    Returns:
        module: The formatter module

    Raises:
        ValueError: If the format is not supported
    """
    if format_name == "json":
        from serverinspector.formatters.json_formatter import JSONFormatter

        return JSONFormatter()

    elif format_name == "yaml":
        from serverinspector.formatters.yaml_formatter import YAMLFormatter

        return YAMLFormatter()

    elif format_name == "html":
        from serverinspector.formatters.html_formatter import HTMLFormatter

        return HTMLFormatter()

    elif format_name == "terminal":
        from serverinspector.formatters.terminal_formatter import TerminalFormatter

        return TerminalFormatter()

    else:
        raise ValueError(f"Unsupported format: {format_name}")
