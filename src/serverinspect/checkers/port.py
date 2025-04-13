"""
Port checker module for ServerInspect.

This module provides simple functions to check port-related aspects of a system.
"""

import logging
import subprocess
import re
import socket

logger = logging.getLogger("serverinspect")


def check(params):
    """
    Perform a port check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - port: Port number to check
            - protocol: Protocol to check (tcp or udp, default: tcp)
            - listening: Whether the port should be listening
            - address: Specific address to check (default: any)

    Returns:
        dict: Check result with success/failure and details
    """
    result = {"success": False, "message": "", "details": {}}

    # Required parameters
    if "port" not in params:
        result["message"] = "Missing required parameter: port"
        return result

    # Get port number and validate it
    try:
        port = int(params["port"])
        if port < 1 or port > 65535:
            result["message"] = f"Invalid port number: {port}"
            return result
    except ValueError:
        result["message"] = f"Invalid port number: {params['port']}"
        return result

    result["details"]["port"] = port

    # Get protocol
    protocol = params.get("protocol", "tcp").lower()
    if protocol not in ["tcp", "udp"]:
        result["message"] = f"Invalid protocol: {protocol}"
        return result
    
    result["details"]["protocol"] = protocol

    # Get specific address if provided
    address = params.get("address", "any")
    result["details"]["address"] = address

    # Check if the port is listening
    port_info = _check_port(port, protocol, address)
    result["details"].update(port_info)

    # Check listening status if required
    if "listening" in params:
        expected_listening = params["listening"]
        result["details"]["expected_listening"] = expected_listening

        if port_info["listening"] != expected_listening:
            if expected_listening:
                result["message"] = f"Port {port}/{protocol} is not listening"
            else:
                result["message"] = f"Port {port}/{protocol} is listening but should not be"
            return result

    # All checks passed
    result["success"] = True
    if port_info["listening"]:
        result["message"] = f"Port {port}/{protocol} is listening as expected"
    else:
        result["message"] = f"Port {port}/{protocol} is not listening as expected"

    return result


def run(runner, test_config):
    """
    Run a port test (legacy API for backward compatibility).

    Args:
        runner: A runner instance
        test_config (dict): Test configuration

    Returns:
        dict: Test result in the old format
    """
    # Convert parameters to the new format
    params = {}
    
    # Handle port parameter
    if "port" in test_config:
        params["port"] = test_config["port"]
    
    # Copy other parameters
    if "protocol" in test_config:
        params["protocol"] = test_config["protocol"]
    if "listening" in test_config:
        params["listening"] = test_config["listening"]
    if "address" in test_config:
        params["address"] = test_config["address"]
    
    # Run the check
    result = check(params)
    
    # Convert the result back to the old format
    old_result = {
        "name": test_config.get("name", "Unnamed port test"),
        "type": "port",
        "result": result["success"],
        "details": result["details"]
    }
    
    # Add error message if check failed
    if not result["success"]:
        old_result["details"]["error"] = result["message"]
    
    return old_result


def _check_port(port, protocol="tcp", address="any"):
    """
    Check if a port is listening.

    Args:
        port (int): Port number
        protocol (str): Protocol (tcp or udp)
        address (str): Specific address to check

    Returns:
        dict: Port information
    """
    port_info = {
        "listening": False,
        "processes": [],
    }

    try:
        # Try to use ss command (modern socket statistics)
        if _command_exists("ss"):
            cmd = ["ss", "-l", "-n"]
            if protocol == "tcp":
                cmd.append("-t")
            elif protocol == "udp":
                cmd.append("-u")

            process = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if process.returncode == 0:
                for line in process.stdout.splitlines():
                    # Look for the port in the output
                    pattern = fr":{port}\b"
                    if re.search(pattern, line):
                        if address == "any" or address in line:
                            port_info["listening"] = True
                            port_info["command_output"] = line.strip()
                            break

        # Fallback to netstat if ss is not available
        elif _command_exists("netstat"):
            cmd = ["netstat", "-l", "-n"]
            if protocol == "tcp":
                cmd.append("-t")
            elif protocol == "udp":
                cmd.append("-u")

            process = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if process.returncode == 0:
                for line in process.stdout.splitlines():
                    # Look for the port in the output
                    pattern = fr":{port}\b"
                    if re.search(pattern, line):
                        if address == "any" or address in line:
                            port_info["listening"] = True
                            port_info["command_output"] = line.strip()
                            break

        # If neither ss nor netstat worked, try a direct socket connection for TCP
        elif protocol == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            port_info["listening"] = result == 0

        # Get the process using the port if it's listening
        if port_info["listening"] and (_command_exists("lsof") or _command_exists("fuser")):
            if _command_exists("lsof"):
                cmd = ["lsof", f"-i:{port}"]
                process = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if process.returncode == 0:
                    # Get process info from lsof output
                    lines = process.stdout.strip().split("\n")[1:]  # Skip header
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            port_info["processes"].append({
                                "name": parts[0],
                                "pid": parts[1],
                            })
            elif _command_exists("fuser"):
                cmd = ["fuser", f"{port}/{protocol}"]
                process = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if process.returncode == 0:
                    # Get process PIDs from fuser output
                    pids = process.stdout.strip().split()
                    for pid in pids:
                        if pid.isdigit():
                            try:
                                # Get process name from /proc
                                with open(f"/proc/{pid}/comm", "r") as f:
                                    name = f.read().strip()
                                    port_info["processes"].append({
                                        "name": name,
                                        "pid": pid,
                                    })
                            except Exception:
                                port_info["processes"].append({"pid": pid})

    except Exception as e:
        logger.error(f"Error checking port {port}/{protocol}: {str(e)}")

    return port_info


def _command_exists(command):
    """Check if a command exists on the system."""
    try:
        subprocess.run(
            ["which", command], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return True
    except Exception:
        return False
