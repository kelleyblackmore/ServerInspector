"""
Port test type for ServerInspect.
"""

import logging
from serverinspect.test_types.base import run_test

logger = logging.getLogger("serverinspect")


def run(runner, test_config):
    """
    Run a port test.

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result
    """
    return run_test(runner, test_config, _run_port_test)


def _run_port_test(runner, test_config):
    """
    Execute a port test.

    Supported test options:
    - port: Port number to check
    - listening: Whether the port should be listening
    - protocol: Protocol to check (tcp, udp)
    - process: Process name that should be using the port

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result
    """
    result = {"result": True, "details": {}}

    # Required parameters
    if "port" not in test_config:
        raise ValueError("Port test requires 'port' parameter")

    port = test_config["port"]
    result["details"]["port"] = port

    # Default protocol is tcp
    protocol = test_config.get("protocol", "tcp")
    result["details"]["protocol"] = protocol

    # Check if port is listening
    cmd = f"ss -ln{protocol[0]} | grep ':{port}'"
    exit_code, stdout, stderr = runner.run_command_with_status(cmd)
    port_listening = exit_code == 0
    result["details"]["listening"] = port_listening

    # If we're checking that a port should be listening or not
    if "listening" in test_config:
        expected_listening = test_config["listening"]
        result["details"]["expected_listening"] = expected_listening

        if port_listening != expected_listening:
            result["result"] = False
            if expected_listening:
                result["details"]["error"] = f"Port {port}/{protocol} is not listening"
            else:
                result["details"][
                    "error"
                ] = f"Port {port}/{protocol} is listening but should not be"

    # Check if the expected process is using the port
    if "process" in test_config and port_listening:
        expected_process = test_config["process"]
        result["details"]["expected_process"] = expected_process

        # Use lsof to check which process has the port open
        process_check_cmd = f"lsof -i {protocol}:{port} -sTCP:LISTEN -t | xargs -r ps -p | grep -v PID | awk '{{print $4}}'"
        actual_process = runner.run_command(process_check_cmd).strip()
        result["details"]["actual_process"] = (
            actual_process if actual_process else "None"
        )

        if expected_process not in actual_process:
            result["result"] = False
            result["details"][
                "error"
            ] = f"Port {port}/{protocol} is used by '{actual_process}' instead of '{expected_process}'"

    return result
