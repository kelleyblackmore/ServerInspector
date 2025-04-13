"""
Command checker module for ServerInspect.

This module provides simple functions to run and check commands on a system.
"""

import subprocess
import logging
import shlex

logger = logging.getLogger("serverinspect")


def check(params):
    """
    Perform a command check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - command: Command to run
            - exit_code: Expected exit code
            - stdout_contains: Text that should be in standard output
            - stderr_contains: Text that should be in standard error

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

    # Run the command
    try:
        # Split the command if it's not already a list
        cmd_args = command if isinstance(command, list) else shlex.split(command)

        # Run the command with timeout
        process = subprocess.run(
            cmd_args, capture_output=True, text=True, timeout=30  # 30 second timeout
        )

        # Store command results
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        exit_code = process.returncode

        result["details"]["exit_code"] = exit_code
        result["details"]["stdout"] = stdout[:200] + (
            "..." if len(stdout) > 200 else ""
        )
        result["details"]["stderr"] = stderr[:200] + (
            "..." if len(stderr) > 200 else ""
        )

        # Check exit code if required
        if "exit_code" in params:
            expected_exit_code = params["exit_code"]
            result["details"]["expected_exit_code"] = expected_exit_code

            if exit_code != expected_exit_code:
                result["message"] = (
                    f"Command exited with code {exit_code}, expected {expected_exit_code}"
                )
                return result

        # Check stdout if required
        if "stdout_contains" in params:
            expected_stdout = params["stdout_contains"]
            result["details"]["expected_stdout_contains"] = expected_stdout

            if expected_stdout not in stdout:
                result["message"] = (
                    f"Command stdout does not contain '{expected_stdout}'"
                )
                return result

        # Check stderr if required
        if "stderr_contains" in params:
            expected_stderr = params["stderr_contains"]
            result["details"]["expected_stderr_contains"] = expected_stderr

            if expected_stderr not in stderr:
                result["message"] = (
                    f"Command stderr does not contain '{expected_stderr}'"
                )
                return result

        # All checks passed
        result["success"] = True
        result["message"] = f"Command '{cmd_args[0]}' passed all checks"

    except subprocess.TimeoutExpired:
        result["message"] = f"Command timed out after 30 seconds: {command}"
        result["details"]["error"] = "timeout"
    except Exception as e:
        result["message"] = f"Error running command: {str(e)}"
        result["details"]["error"] = str(e)

    return result
