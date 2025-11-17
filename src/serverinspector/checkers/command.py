"""
Command checker module for serverinspector.

This module provides simple functions to check command execution on a system.
"""

import logging
import re
import shlex
import subprocess

logger = logging.getLogger("serverinspector")


def check(params):
    """
    Perform a command check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - command: Command to execute
            - exit_code: Expected exit code
            - stdout_contains: Text that should be in the command output
            - stdout_pattern: Regex pattern that should match the command output
            - stderr_contains: Text that should be in the command error output
            - stderr_pattern: Regex pattern that should match the command error output
            - timeout: Command execution timeout in seconds (default: 60)

    Returns:
        dict: Check result with success/failure and details
    """
    result = {"success": False, "message": "", "details": {}}

    # Required parameters
    if "command" not in params:
        result["message"] = "Missing required parameter: command"
        return result

    command = params["command"]
    result["details"]["command"] = command

    # Get timeout
    timeout = params.get("timeout", 60)
    result["details"]["timeout"] = timeout

    # Execute the command
    try:
        # Run the command using subprocess
        # Split the command into arguments to avoid shell=True
        if isinstance(command, str):
            command_args = shlex.split(command)
        else:
            command_args = command

        process = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=True,
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            exit_code = -1
            result["details"]["timeout_expired"] = True

        # Store the results
        result["details"]["exit_code"] = exit_code
        result["details"]["stdout"] = stdout
        result["details"]["stderr"] = stderr

        # Check exit code if specified
        if "exit_code" in params:
            expected_exit_code = params["exit_code"]
            result["details"]["expected_exit_code"] = expected_exit_code

            if exit_code != expected_exit_code:
                result["message"] = (
                    f"Command exited with code {exit_code}, expected {expected_exit_code}"
                )
                return result

        # Check stdout content if specified
        if "stdout_contains" in params:
            expected_content = params["stdout_contains"]
            result["details"]["expected_stdout_contains"] = expected_content

            if expected_content not in stdout:
                result["message"] = (
                    f"Command stdout does not contain: {expected_content}"
                )
                return result

        # Check stdout pattern if specified
        if "stdout_pattern" in params:
            pattern = params["stdout_pattern"]
            result["details"]["stdout_pattern"] = pattern

            if not re.search(pattern, stdout):
                result["message"] = f"Command stdout does not match pattern: {pattern}"
                return result

        # Check stderr content if specified
        if "stderr_contains" in params:
            expected_content = params["stderr_contains"]
            result["details"]["expected_stderr_contains"] = expected_content

            if expected_content not in stderr:
                result["message"] = (
                    f"Command stderr does not contain: {expected_content}"
                )
                return result

        # Check stderr pattern if specified
        if "stderr_pattern" in params:
            pattern = params["stderr_pattern"]
            result["details"]["stderr_pattern"] = pattern

            if not re.search(pattern, stderr):
                result["message"] = f"Command stderr does not match pattern: {pattern}"
                return result

        # All checks passed
        result["success"] = True
        result["message"] = f"Command '{command}' passed all checks"

    except Exception as e:
        result["message"] = f"Error executing command: {str(e)}"
        result["details"]["error"] = str(e)

    return result


def run(_runner, test_config):
    """
    Run a command test (legacy API for backward compatibility).

    Args:
        _runner: A runner instance (unused, kept for API compatibility)
        test_config (dict): Test configuration

    Returns:
        dict: Test result in the old format
    """
    # Convert parameters to the new format
    params = {"command": test_config.get("command")}

    # Copy other parameters
    if "exit_status" in test_config:
        params["exit_code"] = test_config["exit_status"]
    elif "exit_code" in test_config:
        params["exit_code"] = test_config["exit_code"]

    # Handle stdout/stderr checks
    if "stdout" in test_config and isinstance(test_config["stdout"], dict):
        if "contains" in test_config["stdout"]:
            params["stdout_contains"] = test_config["stdout"]["contains"]
        if "pattern" in test_config["stdout"]:
            params["stdout_pattern"] = test_config["stdout"]["pattern"]

    if "stderr" in test_config and isinstance(test_config["stderr"], dict):
        if "contains" in test_config["stderr"]:
            params["stderr_contains"] = test_config["stderr"]["contains"]
        if "pattern" in test_config["stderr"]:
            params["stderr_pattern"] = test_config["stderr"]["pattern"]

    # Handle timeout
    if "timeout" in test_config:
        params["timeout"] = test_config["timeout"]

    # Run the check with our local subprocess instead of using the runner
    result = check(params)

    # Convert the result back to the old format
    old_result = {
        "name": test_config.get("name", "Unnamed command test"),
        "type": "command",
        "result": result["success"],
        "details": result["details"],
    }

    # Add error message if check failed
    if not result["success"]:
        old_result["details"]["error"] = result["message"]

    return old_result
