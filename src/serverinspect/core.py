"""
Core functionality for ServerInspect.
"""

import logging
from datetime import datetime

from serverinspect.checkers import get_checker
from serverinspect.collectors.system_info import collect_system_info
from serverinspect.formatters import get_formatter
from serverinspect.runners import get_runner

logger = logging.getLogger("serverinspect")


class ServerInspect:
    """
    Main class for the ServerInspect tool.
    """

    def __init__(
        self, config=None, host=None, username=None, key_file=None, password=None
    ):
        """
        Initialize ServerInspect with the given configuration.

        Args:
            config (dict): The test configuration
            host (str): Remote host to connect to (None for local)
            username (str): SSH username for remote host
            key_file (str): Path to SSH key file
            password (str): SSH password
        """
        self.config = config or {}
        self.host = host
        self.username = username
        self.key_file = key_file
        self.password = password

        # Get the appropriate runner
        self.runner = get_runner(host, username, key_file, password)

        logger.debug(
            f"Initialized ServerInspect with runner: {self.runner.__class__.__name__}"
        )

    def collect_system_info(self):
        """
        Collect system information using the current runner.

        Returns:
            dict: System information
        """
        logger.debug("Collecting system information")
        return collect_system_info(self.runner)

    def run_tests(self):
        """
        Run all tests defined in the configuration.

        Returns:
            dict: Test results
        """
        if not self.config or "tests" not in self.config:
            raise ValueError("No tests defined in configuration")

        logger.info(f"Running {len(self.config['tests'])} tests...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "host": self.host or "localhost",
            "summary": {"total": len(self.config["tests"]), "passed": 0, "failed": 0},
            "tests": [],
        }

        # Add metadata if available
        if "title" in self.config:
            results["title"] = self.config["title"]
        if "description" in self.config:
            results["description"] = self.config["description"]

        system_info = self.collect_system_info()
        results["system_info"] = system_info

        for test_config in self.config["tests"]:
            try:
                logger.debug(f"Running test: {test_config['name']}")

                # Get the appropriate test handler
                test_type = test_config["type"]
                checker_module = get_checker(test_type)

                # Run the test
                test_result = checker_module.run(self.runner, test_config)

                # Update summary
                if test_result["result"]:
                    results["summary"]["passed"] += 1
                else:
                    results["summary"]["failed"] += 1

                # Add to results
                results["tests"].append(test_result)

                # Log result
                status = "✅ PASS" if test_result["result"] else "❌ FAIL"
                logger.info(f"{status} - {test_result['name']}")

            except Exception as e:
                logger.error(
                    f"Error running test {test_config.get('name', 'unknown')}: {str(e)}"
                )
                test_result = {
                    "name": test_config.get("name", "unknown"),
                    "type": test_config.get("type", "unknown"),
                    "result": False,
                    "error": str(e),
                }
                results["tests"].append(test_result)
                results["summary"]["failed"] += 1

        logger.info(
            f"Tests completed: {results['summary']['passed']} passed, "
            f"{results['summary']['failed']} failed"
        )

        return results

    def output_results(self, results, format="terminal", output_file=None):
        """
        Output the test results in the specified format.

        Args:
            results (dict): Test results
            format (str): Output format (json, yaml, html, terminal)
            output_file (str): Output file path (None for stdout)
        """
        logger.debug(f"Outputting results in {format} format")

        formatter = get_formatter(format)
        output = formatter.format(results)

        if output_file:
            with open(output_file, "w") as f:
                f.write(output)
            logger.info(f"Results written to {output_file}")
        else:
            # For terminal output, this is already handled by the formatter
            if format != "terminal":
                print(output)
