"""
Base runner for ServerInspect.

This module provides the base class for all runners, containing shared
logic for service, package, and process status checks.
"""

import logging
from abc import ABC, abstractmethod

from serverinspect.package_managers import get_registry
from serverinspect.service_managers import get_service_status as get_enhanced_service_status

logger = logging.getLogger("serverinspect")


class BaseRunner(ABC):
    """
    Abstract base class for all runners.
    
    Subclasses must implement the run_command and run_command_with_status methods.
    All high-level operations (service_status, package_status, process_status)
    are implemented here and use the abstract command execution methods.
    """

    @abstractmethod
    def run_command(self, command):
        """
        Run a command and return its output.

        Args:
            command (str): Command to run

        Returns:
            str: Command output (stdout)
        """
        pass

    @abstractmethod
    def run_command_with_status(self, command):
        """
        Run a command and return both output and exit status.

        Args:
            command (str): Command to run

        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        pass

    @abstractmethod
    def file_exists(self, path):
        """
        Check if a file exists.

        Args:
            path (str): Path to check

        Returns:
            bool: True if the file exists
        """
        pass

    def service_status(self, service_name, enhanced=True):
        """
        Check the status of a service with optional enhanced details.

        Args:
            service_name (str): Name of the service
            enhanced (bool): If True, return rich ServiceStatus details

        Returns:
            dict: Service status information with keys:
                - exists (bool): Whether the service exists
                - running (bool): Whether the service is running
                - enabled (bool): Whether the service is enabled
                - state (str): Service state (if enhanced)
                - substate (str): Service substate (if enhanced)
                - loaded (bool): Whether service is loaded (if enhanced)
                - masked (bool): Whether service is masked (if enhanced)
                - restart_count (int): Number of restarts (if enhanced)
                - pid (int): Main process ID (if enhanced)
                - memory_usage (str): Memory usage (if enhanced)
                - uptime (str): Service uptime (if enhanced)
                - dependencies (list): Service dependencies (if enhanced)
                - service_manager (str): Service manager used
                - error (str): Error message if any
        """
        if enhanced:
            # Use the enhanced service manager
            status_obj = get_enhanced_service_status(self, service_name)
            return status_obj.to_dict()
        else:
            # Use legacy basic check for backward compatibility
            return self._basic_service_status(service_name)

    def _basic_service_status(self, service_name):
        """
        Basic service status check (legacy method).
        
        This is kept for backward compatibility and as a fallback.
        """
        result = {"exists": False, "running": False, "enabled": False, "error": None}

        # Try systemctl first (systemd)
        exit_code, _, _ = self.run_command_with_status("which systemctl")
        if exit_code == 0:
            try:
                # Check if service exists
                exit_code, _, _ = self.run_command_with_status(
                    f"systemctl list-unit-files | grep -q {service_name}.service"
                )
                result["exists"] = exit_code == 0

                if result["exists"]:
                    # Check if service is running
                    exit_code, _, _ = self.run_command_with_status(
                        f"systemctl is-active --quiet {service_name}"
                    )
                    result["running"] = exit_code == 0

                    # Check if service is enabled
                    exit_code, _, _ = self.run_command_with_status(
                        f"systemctl is-enabled --quiet {service_name}"
                    )
                    result["enabled"] = exit_code == 0

                return result
            except Exception as e:
                result["error"] = str(e)
                logger.debug(f"Error checking service with systemctl: {str(e)}")

        # Try service command (SysV init)
        exit_code, _, _ = self.run_command_with_status("which service")
        if exit_code == 0:
            try:
                # Check if service exists
                exit_code, _, _ = self.run_command_with_status(
                    f"service {service_name} status"
                )
                result["exists"] = exit_code != 127  # 127 = command not found

                if result["exists"]:
                    # Parsing the output to determine if it's running
                    _, stdout, _ = self.run_command_with_status(
                        f"service {service_name} status"
                    )
                    result["running"] = "running" in stdout.lower()

                    # Check if service is enabled (might not work on all systems)
                    exit_code, _, _ = self.run_command_with_status("ls /etc/init.d")
                    if exit_code == 0:
                        for i in range(2, 6):  # Check runlevels 2-5
                            exit_code, stdout, _ = self.run_command_with_status(
                                f"ls /etc/rc{i}.d/S*{service_name} 2>/dev/null || ls /etc/rc.d/rc{i}.d/S*{service_name} 2>/dev/null"
                            )
                            if exit_code == 0 and stdout.strip():
                                result["enabled"] = True
                                break

                return result
            except Exception as e:
                if not result["error"]:  # Don't overwrite systemctl error
                    result["error"] = str(e)
                logger.debug(f"Error checking service with service command: {str(e)}")

        # If we get here, we couldn't check the service
        if not result["error"]:
            result["error"] = (
                "Could not determine service status (no systemctl or service command found)"
            )

        return result

    def package_status(self, package_name, package_manager=None):
        """
        Check if a package is installed using the package manager registry.

        Args:
            package_name (str): Name of the package
            package_manager (str): Specific package manager to use (optional)

        Returns:
            dict: Package status information with keys:
                - installed (bool): Whether the package is installed
                - version (str): Package version if installed
                - package_manager (str): Package manager used
                - error (str): Error message if any
        """
        try:
            registry = get_registry()
            result = registry.check_package(self, package_name, package_manager)
            
            # Add error if package not found
            if not result["installed"] and not result.get("error"):
                if package_manager:
                    result["error"] = f"Package '{package_name}' not found using {package_manager}"
                else:
                    managers = registry.detect_available(self)
                    if managers:
                        result["error"] = f"Package '{package_name}' not found in any package manager"
                    else:
                        result["error"] = "No supported package manager found"
            
            return result
        except Exception as e:
            logger.error(f"Error checking package status: {str(e)}")
            return {
                "installed": False,
                "version": None,
                "package_manager": None,
                "error": str(e),
            }

    def process_status(self, process_name):
        """
        Check if a process is running.

        Args:
            process_name (str): Name of the process

        Returns:
            dict: Process status information with keys:
                - running (bool): Whether any instance is running
                - count (int): Number of instances running
                - pids (list): Process IDs if available
                - commands (list): Command lines if available
                - error (str): Error message if any
        """
        result = {
            "running": False,
            "count": 0,
            "pids": [],
            "commands": [],
            "error": None,
        }

        try:
            # Try pgrep first (most reliable and portable)
            exit_code, _, _ = self.run_command_with_status("which pgrep")
            if exit_code == 0:
                # Get process count
                exit_code, stdout, _ = self.run_command_with_status(
                    f"pgrep -c -f '{process_name}'"
                )
                if exit_code in (0, 1):  # 0 = found, 1 = not found
                    count = int(stdout.strip()) if stdout.strip() else 0
                    result["count"] = count
                    result["running"] = count > 0

                    # Get PIDs if running
                    if result["running"]:
                        exit_code, stdout, _ = self.run_command_with_status(
                            f"pgrep -f '{process_name}'"
                        )
                        if exit_code == 0 and stdout.strip():
                            result["pids"] = stdout.strip().split("\n")

                        # Get command lines
                        if result["pids"]:
                            for pid in result["pids"]:
                                exit_code, stdout, _ = self.run_command_with_status(
                                    f"ps -p {pid} -o cmd= 2>/dev/null"
                                )
                                if exit_code == 0 and stdout.strip():
                                    result["commands"].append(stdout.strip())

                return result

            # Fallback to ps + grep
            exit_code, stdout, _ = self.run_command_with_status(
                f"ps aux | grep -v grep | grep '{process_name}'"
            )
            if exit_code in (0, 1):  # 0 = found, 1 = not found
                lines = [line for line in stdout.splitlines() if line.strip()]
                result["count"] = len(lines)
                result["running"] = result["count"] > 0

                # Extract PIDs and commands from ps output
                for line in lines:
                    parts = line.split(None, 10)  # Split on whitespace, max 11 parts
                    if len(parts) >= 2:
                        result["pids"].append(parts[1])  # PID is second column
                    if len(parts) >= 11:
                        result["commands"].append(parts[10])  # Command is last

                return result

        except ValueError as e:
            result["error"] = f"Error parsing process output: {str(e)}"
            logger.debug(result["error"])
        except Exception as e:
            result["error"] = str(e)
            logger.debug(f"Error checking process: {str(e)}")

        return result
