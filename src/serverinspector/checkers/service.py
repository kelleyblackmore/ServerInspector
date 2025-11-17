"""
Service checker module for serverinspector.

This module provides simple functions to check service-related aspects of a system.
"""

import logging
import shutil
import subprocess

logger = logging.getLogger("serverinspector")


def check(params):
    """
    Perform a service check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - service: Name of the service to check
            - running: Whether the service should be running
            - enabled: Whether the service should be enabled to start on boot

    Returns:
        dict: Check result with success/failure and details
    """
    result = {"success": False, "message": "", "details": {}}

    # Required parameters
    if "service" not in params:
        result["message"] = "Missing required parameter: service"
        return result

    service_name = params["service"]
    result["details"]["service"] = service_name

    # Get service status
    service_info = _get_service_status(service_name)
    result["details"].update(service_info)

    # Check if the service exists
    if not service_info["exists"]:
        result["message"] = f"Service '{service_name}' does not exist"
        return result

    # Check if the service is running
    if "running" in params:
        expected_running = params["running"]
        result["details"]["expected_running"] = expected_running

        if service_info["running"] != expected_running:
            if expected_running:
                result["message"] = f"Service '{service_name}' is not running"
            else:
                result["message"] = (
                    f"Service '{service_name}' is running but should not be"
                )
            return result

    # Check if the service is enabled
    if "enabled" in params:
        expected_enabled = params["enabled"]
        result["details"]["expected_enabled"] = expected_enabled

        if service_info["enabled"] != expected_enabled:
            if expected_enabled:
                result["message"] = f"Service '{service_name}' is not enabled"
            else:
                result["message"] = (
                    f"Service '{service_name}' is enabled but should not be"
                )
            return result

    # If we've made it this far, all checks have passed
    result["success"] = True
    result["message"] = f"Service '{service_name}' passed all checks"

    return result


def run(_runner, test_config):
    """
    Run a service test (legacy API for backward compatibility).

    Args:
        _runner: A runner instance (unused, kept for API compatibility)
        test_config (dict): Test configuration

    Returns:
        dict: Test result in the old format
    """
    # Convert parameters to the new format
    params = {"service": test_config.get("service")}

    # Copy other parameters
    if "running" in test_config:
        params["running"] = test_config["running"]
    if "enabled" in test_config:
        params["enabled"] = test_config["enabled"]

    # Run the check
    result = check(params)

    # Convert the result back to the old format
    old_result = {
        "name": test_config.get("name", "Unnamed service test"),
        "type": "service",
        "result": result["success"],
        "details": result["details"],
    }

    # Add error message if check failed
    if not result["success"]:
        old_result["details"]["error"] = result["message"]

    return old_result


def _get_service_status(service_name):
    """
    Get the status of a systemd service.

    Args:
        service_name (str): Name of the service

    Returns:
        dict: Service status info
    """
    service_info = {"exists": False, "running": False, "enabled": False}

    # Detect service manager
    if shutil.which("systemctl"):
        # For systemd-based systems
        try:
            # Check if service exists
            proc = subprocess.run(
                ["/usr/bin/systemctl", "list-unit-files", f"{service_name}.service"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            service_info["exists"] = (
                proc.returncode == 0 and f"{service_name}.service" in proc.stdout
            )

            if service_info["exists"]:
                # Check if service is running
                proc = subprocess.run(
                    ["/usr/bin/systemctl", "is-active", f"{service_name}.service"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                service_info["running"] = (
                    proc.returncode == 0 and proc.stdout.strip() == "active"
                )

                # Check if service is enabled
                proc = subprocess.run(
                    ["/usr/bin/systemctl", "is-enabled", f"{service_name}.service"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                service_info["enabled"] = (
                    proc.returncode == 0 and proc.stdout.strip() == "enabled"
                )
        except Exception as e:
            logger.error(f"Error getting systemd service status: {str(e)}")
    elif shutil.which("service"):
        # For init.d based systems
        try:
            # Check if service exists
            proc = subprocess.run(
                ["/usr/sbin/service", "--status-all"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output = proc.stdout + proc.stderr
            service_info["exists"] = any(
                line.endswith(f" {service_name}") for line in output.split("\n")
            )

            if service_info["exists"]:
                # Check if service is running
                proc = subprocess.run(
                    ["/usr/sbin/service", service_name, "status"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                service_info["running"] = (
                    proc.returncode == 0 and "running" in proc.stdout.lower()
                )

                # Check if service is enabled (we check for symlinks in /etc/rc*.d)
                proc = subprocess.run(
                    ["/usr/bin/find", "/etc/rc*.d", "-name", f"S*{service_name}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                service_info["enabled"] = proc.stdout.strip() != ""
        except Exception as e:
            logger.error(f"Error getting service status: {str(e)}")

    return service_info
