"""
Process checker module for ServerInspect.

This module provides simple functions to check process-related aspects of a system.
"""

import logging
import re
import shutil
import subprocess

logger = logging.getLogger("serverinspect")


def check(params):
    """
    Perform a process check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - process_name: Name of the process to check
            - running: Whether the process should be running
            - min_count: Minimum number of instances (default: 1)
            - max_count: Maximum number of instances
            - command_pattern: Regex pattern to match against the full command line

    Returns:
        dict: Check result with success/failure and details
    """
    result = {"success": False, "message": "", "details": {}}

    # Required parameters
    if "process_name" not in params and "process" not in params:
        result["message"] = "Missing required parameter: process_name"
        return result

    # Support both process_name and process for backward compatibility
    process_name = params.get("process_name", params.get("process"))
    result["details"]["process_name"] = process_name

    # Get process information
    process_info = _get_process_info(process_name, params.get("command_pattern"))
    result["details"].update(process_info)

    # Check if the process is running
    if "running" in params:
        expected_running = params["running"]
        result["details"]["expected_running"] = expected_running

        if process_info["running"] != expected_running:
            if expected_running:
                result["message"] = f"Process '{process_name}' is not running"
            else:
                result[
                    "message"
                ] = f"Process '{process_name}' is running but should not be"
            return result

    # If we're checking that process should not be running and it's not
    if "running" in params and not params["running"] and not process_info["running"]:
        result["success"] = True
        result["message"] = f"Process '{process_name}' is not running as expected"
        return result

    # Only do these checks if the process is running
    if process_info["running"]:
        # Check minimum instance count if specified
        if "min_count" in params:
            min_count = params["min_count"]
            result["details"]["min_count"] = min_count

            if process_info["count"] < min_count:
                result[
                    "message"
                ] = f"Process '{process_name}' has {process_info['count']} instances, expected at least {min_count}"
                return result

        # Check maximum instance count if specified
        if "max_count" in params:
            max_count = params["max_count"]
            result["details"]["max_count"] = max_count

            if process_info["count"] > max_count:
                result[
                    "message"
                ] = f"Process '{process_name}' has {process_info['count']} instances, expected at most {max_count}"
                return result

        # All checks passed
        result["success"] = True
        result[
            "message"
        ] = f"Process '{process_name}' passed all checks (running with {process_info['count']} instances)"
    else:
        # Process not running, but that was expected or not specified
        result["success"] = True
        result[
            "message"
        ] = f"Process '{process_name}' is not running (as expected or not specified)"

    return result


def run(runner, test_config):
    """
    Run a process test (legacy API for backward compatibility).

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result in the old format
    """
    # Convert parameters to the new format
    params = {}

    # Support both process_name and process parameters
    if "process_name" in test_config:
        params["process_name"] = test_config["process_name"]
    elif "process" in test_config:
        params["process_name"] = test_config["process"]

    # Copy other parameters
    if "running" in test_config:
        params["running"] = test_config["running"]
    if "min_count" in test_config:
        params["min_count"] = test_config["min_count"]
    if "max_count" in test_config:
        params["max_count"] = test_config["max_count"]
    if "command_pattern" in test_config:
        params["command_pattern"] = test_config["command_pattern"]

    # Run the check
    result = check(params)

    # Convert the result back to the old format
    old_result = {
        "name": test_config.get("name", "Unnamed process test"),
        "type": "process",
        "result": result["success"],
        "details": result["details"],
    }

    # Add error message if check failed
    if not result["success"]:
        old_result["details"]["error"] = result["message"]

    return old_result


def _get_process_info(process_name, command_pattern=None):
    """
    Get information about a process.

    Args:
        process_name (str): Name of the process
        command_pattern (str): Optional regex pattern to match against command line

    Returns:
        dict: Process information
    """
    process_info = {"running": False, "count": 0, "pids": [], "commands": []}

    try:
        # Try to use pgrep first (most reliable for name matching)
        if shutil.which("pgrep"):
            # Get PIDs using pgrep
            proc = subprocess.run(
                ["/usr/bin/pgrep", "-f", process_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if proc.returncode == 0:
                pids = proc.stdout.strip().split("\n")
                process_info["running"] = True
                process_info["count"] = len(pids)
                process_info["pids"] = pids

                # Get command lines for each PID
                for pid in pids:
                    try:
                        cmd_proc = subprocess.run(
                            ["/bin/ps", "-p", pid, "-o", "cmd="],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )
                        if cmd_proc.returncode == 0:
                            cmd = cmd_proc.stdout.strip()
                            process_info["commands"].append(cmd)

                            # If command pattern is specified, check if it matches
                            if command_pattern and not re.search(command_pattern, cmd):
                                # Remove this PID if command doesn't match the pattern
                                process_info["count"] -= 1
                                process_info["pids"].remove(pid)
                    except (subprocess.SubprocessError, ValueError) as e:
                        logger.error(f"Error getting command for PID {pid}: {str(e)}")

                # Update running status based on final count
                process_info["running"] = process_info["count"] > 0

        # Fall back to ps if pgrep is not available
        elif shutil.which("ps"):
            proc = subprocess.run(
                ["/bin/ps", "-eo", "pid,comm,cmd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if proc.returncode == 0:
                lines = proc.stdout.strip().split("\n")[1:]  # Skip header
                matching_processes = []

                for line in lines:
                    if process_name in line:
                        parts = line.strip().split(None, 2)
                        if len(parts) >= 3:
                            pid, comm, cmd = parts

                            # If command pattern is specified, check if it matches
                            if command_pattern and not re.search(command_pattern, cmd):
                                continue

                            matching_processes.append({"pid": pid, "command": cmd})
                            process_info["pids"].append(pid)
                            process_info["commands"].append(cmd)

                process_info["count"] = len(matching_processes)
                process_info["running"] = process_info["count"] > 0

    except (subprocess.SubprocessError, OSError) as e:
        logger.error(f"Error checking process '{process_name}': {str(e)}")

    return process_info
