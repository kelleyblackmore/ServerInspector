"""
Command test type for ServerInspect.
"""

import logging
import re
from serverinspect.test_types.base import run_test

logger = logging.getLogger("serverinspect")


def run(runner, test_config):
    """
    Run a command test.

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result
    """
    return run_test(runner, test_config, _run_command_test)


def _run_command_test(runner, test_config):
    """
    Execute a command test.

    Supported test options:
    - command: Command to run
    - exit_status: Expected exit status
    - stdout: Content checks for standard output
      - contains: Text that should be in the output
      - matches: Regex pattern that should match the output
      - equals: Exact text that the output should equal
    - stderr: Content checks for standard error (same options as stdout)

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result
    """
    result = {"result": True, "details": {}}

    # Required parameters
    if "command" not in test_config:
        raise ValueError("Command test requires 'command' parameter")

    command = test_config["command"]
    result["details"]["command"] = command

    # Run the command
    exit_code, stdout, stderr = runner.run_command_with_status(command)
    result["details"]["exit_status"] = exit_code

    # Store stdout and stderr if not too large (prevent huge results)
    if len(stdout) <= 1024:
        result["details"]["stdout"] = stdout
    else:
        result["details"]["stdout"] = stdout[:1021] + "..."

    if len(stderr) <= 1024:
        result["details"]["stderr"] = stderr
    else:
        result["details"]["stderr"] = stderr[:1021] + "..."

    # Check exit status
    if "exit_status" in test_config:
        expected_status = test_config["exit_status"]
        result["details"]["expected_exit_status"] = expected_status

        if exit_code != expected_status:
            result["result"] = False
            result["details"][
                "error"
            ] = f"Expected exit status {expected_status}, got {exit_code}"

    # Check stdout
    if "stdout" in test_config and isinstance(test_config["stdout"], dict):
        stdout_checks = test_config["stdout"]

        # Check for exact match
        if "equals" in stdout_checks:
            expected = stdout_checks["equals"]
            if stdout.strip() != expected:
                result["result"] = False
                result["details"]["error"] = f"Expected stdout to equal '{expected}'"

        # Check for content containment
        if "contains" in stdout_checks:
            expected = stdout_checks["contains"]
            if expected not in stdout:
                result["result"] = False
                result["details"]["error"] = f"Expected stdout to contain '{expected}'"

        # Check for regex match
        if "matches" in stdout_checks:
            pattern = stdout_checks["matches"]
            if not re.search(pattern, stdout):
                result["result"] = False
                result["details"][
                    "error"
                ] = f"Expected stdout to match pattern '{pattern}'"

    # Check stderr
    if "stderr" in test_config and isinstance(test_config["stderr"], dict):
        stderr_checks = test_config["stderr"]

        # Check for exact match
        if "equals" in stderr_checks:
            expected = stderr_checks["equals"]
            if stderr.strip() != expected:
                result["result"] = False
                result["details"]["error"] = f"Expected stderr to equal '{expected}'"

        # Check for content containment
        if "contains" in stderr_checks:
            expected = stderr_checks["contains"]
            if expected not in stderr:
                result["result"] = False
                result["details"]["error"] = f"Expected stderr to contain '{expected}'"

        # Check for regex match
        if "matches" in stderr_checks:
            pattern = stderr_checks["matches"]
            if not re.search(pattern, stderr):
                result["result"] = False
                result["details"][
                    "error"
                ] = f"Expected stderr to match pattern '{pattern}'"

    return result
