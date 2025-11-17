"""
YAML formatter for serverinspector.
"""

import logging

import yaml

from serverinspector.formatters.base import BaseFormatter

logger = logging.getLogger("serverinspector")


class YAMLFormatter(BaseFormatter):
    """
    Formatter that outputs results as YAML.
    """

    def format(self, results):
        """
        Format the test results as YAML.

        Args:
            results (dict): Test results

        Returns:
            str: YAML-formatted results
        """
        logger.debug("Formatting results as YAML")

        return yaml.dump(results, default_flow_style=False, sort_keys=False)
