"""
JSON formatter for serverinspector.
"""

import json
import logging

from serverinspector.formatters.base import BaseFormatter

logger = logging.getLogger("serverinspector")


class JSONFormatter(BaseFormatter):
    """
    Formatter that outputs results as JSON.
    """

    def format(self, results):
        """
        Format the test results as JSON.

        Args:
            results (dict): Test results

        Returns:
            str: JSON-formatted results
        """
        logger.debug("Formatting results as JSON")

        return json.dumps(results, indent=2, sort_keys=True)
