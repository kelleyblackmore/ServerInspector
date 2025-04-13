"""
Package test type for ServerInspect.
"""

import logging
from serverinspect.test_types.base import run_test

logger = logging.getLogger("serverinspect")


def run(runner, test_config):
    """
    Run a package test.

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result
    """
    return run_test(runner, test_config, _run_package_test)


def _run_package_test(runner, test_config):
    """
    Execute a package test.

    Supported test options:
    - package: Name of the package
    - installed: Whether the package should be installed
    - version: Expected package version

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result
    """
    result = {"result": True, "details": {}}

    # Required parameters
    if "package" not in test_config:
        raise ValueError("Package test requires 'package' parameter")

    package_name = test_config["package"]
    result["details"]["package"] = package_name

    # Get package status
    package_info = runner.package_status(package_name)
    result["details"].update(package_info)

    # Check if the package is installed
    if "installed" in test_config:
        expected_installed = test_config["installed"]
        result["details"]["expected_installed"] = expected_installed

        if package_info["installed"] != expected_installed:
            result["result"] = False
            if expected_installed:
                result["details"][
                    "error"
                ] = f"Package '{package_name}' is not installed"
            else:
                result["details"][
                    "error"
                ] = f"Package '{package_name}' is installed but should not be"

    # Check package version
    if "version" in test_config and package_info["installed"]:
        expected_version = test_config["version"]
        result["details"]["expected_version"] = expected_version

        if package_info["version"] != expected_version:
            result["result"] = False
            result["details"][
                "error"
            ] = f"Expected version '{expected_version}', found '{package_info['version']}'"

    return result
