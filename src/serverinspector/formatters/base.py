"""
Base formatter for serverinspector.
"""

import logging

logger = logging.getLogger("serverinspector")


class BaseFormatter:
    """
    Base class for all formatters.
    """

    def format(self, results):
        """
        Format the test results.

        Args:
            results (dict): Test results

        Returns:
            str: Formatted results
        """
        raise NotImplementedError("Formatter must implement format method")
