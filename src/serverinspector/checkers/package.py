"""
Package checker module for serverinspector.

This module provides simple functions to check package-related aspects of a system.
"""

import logging
import shutil
import subprocess

logger = logging.getLogger("serverinspector")


def check(params):
    """
    Perform a package check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - package: Name of the package to check
            - installed: Whether the package should be installed
            - version: Specific version of the package

    Returns:
        dict: Check result with success/failure and details
    """
    result = {"success": False, "message": "", "details": {}}

    # Required parameters
    if "package" not in params:
        result["message"] = "Missing required parameter: package"
        return result

    package_name = params["package"]
    result["details"]["package"] = package_name

    # Get package information
    pkg_info = _get_package_info(package_name)
    result["details"].update(pkg_info)

    # Check if the package exists/is installed
    if "installed" in params:
        expected_installed = params["installed"]
        result["details"]["expected_installed"] = expected_installed

        if pkg_info["installed"] != expected_installed:
            if expected_installed:
                result["message"] = f"Package '{package_name}' is not installed"
            else:
                result["message"] = (
                    f"Package '{package_name}' is installed but should not be"
                )
            return result

    # If we're checking that package should not be installed and it's not
    if "installed" in params and not params["installed"] and not pkg_info["installed"]:
        result["success"] = True
        result["message"] = f"Package '{package_name}' is not installed as expected"
        return result

    # Only do version checks if package is installed
    if pkg_info["installed"] and "version" in params:
        expected_version = params["version"]
        actual_version = pkg_info.get("version", "unknown")
        result["details"]["expected_version"] = expected_version

        if expected_version != actual_version:
            result["message"] = (
                f"Package '{package_name}' version is {actual_version}, expected {expected_version}"
            )
            return result

    # All checks passed
    result["success"] = True
    result["message"] = f"Package '{package_name}' passed all checks"

    return result


def run(_runner, test_config):
    """
    Run a package test (legacy API for backward compatibility).

    Args:
        _runner: A runner instance (unused, kept for API compatibility)
        test_config (dict): Test configuration

    Returns:
        dict: Test result in the old format
    """
    # Convert parameters to the new format
    params = {"package": test_config.get("package")}

    # Copy other parameters
    if "installed" in test_config:
        params["installed"] = test_config["installed"]
    if "version" in test_config:
        params["version"] = test_config["version"]

    # Run the check
    result = check(params)

    # Convert the result back to the old format
    old_result = {
        "name": test_config.get("name", "Unnamed package test"),
        "type": "package",
        "result": result["success"],
        "details": result["details"],
    }

    # Add error message if check failed
    if not result["success"]:
        old_result["details"]["error"] = result["message"]

    return old_result


def _get_package_info(package_name):
    """
    Get information about a package.

    This function tries to detect the package manager and use the appropriate
    commands to get information about the package.

    Args:
        package_name (str): Name of the package

    Returns:
        dict: Package information
    """
    pkg_info = {"installed": False, "version": None, "package_manager": None}

    # Try different package managers
    if shutil.which("dpkg"):
        # Debian/Ubuntu
        pkg_info["package_manager"] = "dpkg"
        try:
            # Check if package is installed
            proc = subprocess.run(
                ["/usr/bin/dpkg", "-s", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            pkg_info["installed"] = proc.returncode == 0

            if pkg_info["installed"]:
                # Get version
                for line in proc.stdout.splitlines():
                    if line.startswith("Version:"):
                        pkg_info["version"] = line.split(":", 1)[1].strip()
                        break
        except subprocess.SubprocessError as e:
            logger.error(f"Error checking dpkg package: {str(e)}")

    elif shutil.which("rpm"):
        # Red Hat/CentOS/Fedora
        pkg_info["package_manager"] = "rpm"
        try:
            # Check if package is installed
            proc = subprocess.run(
                ["/usr/bin/rpm", "-q", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            pkg_info["installed"] = proc.returncode == 0

            if pkg_info["installed"]:
                # Get version - output is typically package-version-release
                output = proc.stdout.strip()
                if output.startswith(package_name):
                    parts = output.split("-")
                    if len(parts) >= 2:
                        pkg_info["version"] = parts[1]
        except subprocess.SubprocessError as e:
            logger.error(f"Error checking rpm package: {str(e)}")

    elif shutil.which("pacman"):
        # Arch Linux
        pkg_info["package_manager"] = "pacman"
        try:
            # Check if package is installed
            proc = subprocess.run(
                ["/usr/bin/pacman", "-Q", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            pkg_info["installed"] = proc.returncode == 0

            if pkg_info["installed"]:
                # Get version - output is typically "package version"
                output = proc.stdout.strip()
                parts = output.split(" ")
                if len(parts) >= 2:
                    pkg_info["version"] = parts[1]
        except subprocess.SubprocessError as e:
            logger.error(f"Error checking pacman package: {str(e)}")

    elif shutil.which("apk"):
        # Alpine Linux
        pkg_info["package_manager"] = "apk"
        try:
            # Check if package is installed
            proc = subprocess.run(
                ["/sbin/apk", "info", "-e", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            pkg_info["installed"] = proc.returncode == 0 and package_name in proc.stdout

            if pkg_info["installed"]:
                # Get version
                version_proc = subprocess.run(
                    ["/sbin/apk", "info", "-v", package_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if version_proc.returncode == 0:
                    output = version_proc.stdout.strip()
                    parts = output.split("-")
                    if len(parts) >= 2:
                        pkg_info["version"] = parts[1]
        except subprocess.SubprocessError as e:
            logger.error(f"Error checking apk package: {str(e)}")

    return pkg_info
