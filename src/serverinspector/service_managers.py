"""
Service manager registry for serverinspector.

This module provides enhanced service management with support for systemd,
SysV init, OpenRC, and other service managers.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger("serverinspector")


@dataclass
class ServiceStatus:
    """
    Rich service status information.
    """

    exists: bool = False
    running: bool = False
    enabled: bool = False
    state: Optional[str] = None  # active, inactive, failed, activating, etc.
    substate: Optional[str] = None  # running, dead, exited, etc.
    loaded: bool = False
    masked: bool = False
    restart_count: int = 0
    pid: Optional[int] = None
    memory_usage: Optional[str] = None
    cpu_usage: Optional[str] = None
    uptime: Optional[str] = None
    service_manager: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    error: Optional[str] = None
    raw_status: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "exists": self.exists,
            "running": self.running,
            "enabled": self.enabled,
            "state": self.state,
            "substate": self.substate,
            "loaded": self.loaded,
            "masked": self.masked,
            "restart_count": self.restart_count,
            "pid": self.pid,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "uptime": self.uptime,
            "service_manager": self.service_manager,
            "dependencies": self.dependencies,
            "error": self.error,
        }


class SystemdManager:
    """
    Enhanced systemd service manager with rich detail support.
    """

    name = "systemd"
    binary = "systemctl"

    @staticmethod
    def detect(runner) -> bool:
        """Check if systemd is available."""
        exit_code, _, _ = runner.run_command_with_status("which systemctl")
        return exit_code == 0

    @staticmethod
    def get_service_status(runner, service_name: str) -> ServiceStatus:
        """
        Get comprehensive service status from systemd.

        Args:
            runner: Runner instance
            service_name: Name of the service

        Returns:
            ServiceStatus object with detailed information
        """
        status = ServiceStatus(service_manager="systemd")

        # Check if service exists
        exit_code, stdout, _ = runner.run_command_with_status(
            f"systemctl list-unit-files {service_name}.service"
        )
        status.exists = exit_code == 0 and f"{service_name}.service" in stdout

        if not status.exists:
            status.error = f"Service '{service_name}' does not exist"
            return status

        # Get detailed status using systemctl show
        exit_code, stdout, _ = runner.run_command_with_status(
            f"systemctl show {service_name}.service"
        )

        if exit_code == 0:
            properties = {}
            for line in stdout.splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    properties[key] = value

            # Parse systemd properties
            status.loaded = properties.get("LoadState") == "loaded"
            status.state = properties.get("ActiveState")
            status.substate = properties.get("SubState")
            status.running = status.state == "active"
            status.masked = properties.get("LoadState") == "masked"

            # Get enabled status
            unit_file_state = properties.get("UnitFileState", "")
            status.enabled = unit_file_state in ["enabled", "enabled-runtime", "static"]

            # Get PID
            main_pid = properties.get("MainPID")
            if main_pid and main_pid != "0":
                status.pid = int(main_pid)

            # Get restart count
            n_restarts = properties.get("NRestarts")
            if n_restarts:
                try:
                    status.restart_count = int(n_restarts)
                except ValueError:
                    pass

            # Get memory usage
            memory = properties.get("MemoryCurrent")
            if memory and memory != "[not set]":
                try:
                    mem_bytes = int(memory)
                    status.memory_usage = SystemdManager._format_bytes(mem_bytes)
                except ValueError:
                    status.memory_usage = memory

            # Get dependencies
            wants = properties.get("Wants", "")
            requires = properties.get("Requires", "")
            deps = []
            if wants:
                deps.extend(wants.split())
            if requires:
                deps.extend(requires.split())
            status.dependencies = list(set(deps))  # Remove duplicates

        # Get human-readable status
        exit_code, stdout, _ = runner.run_command_with_status(
            f"systemctl status {service_name}.service"
        )
        status.raw_status = stdout if exit_code in (0, 3) else None

        # Try to extract uptime from status output
        if status.raw_status:
            uptime_match = re.search(r"Active:.*since ([^;]+);", status.raw_status)
            if uptime_match:
                status.uptime = uptime_match.group(1)

        return status

    @staticmethod
    def _format_bytes(bytes_value: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"

    @staticmethod
    def get_service_logs(runner, service_name: str, lines: int = 50) -> List[str]:
        """
        Get recent service logs from journalctl.

        Args:
            runner: Runner instance
            service_name: Name of the service
            lines: Number of log lines to retrieve

        Returns:
            List of log lines
        """
        exit_code, stdout, _ = runner.run_command_with_status(
            f"journalctl -u {service_name}.service -n {lines} --no-pager"
        )

        if exit_code == 0:
            return stdout.splitlines()
        return []


class SysVManager:
    """
    SysV init service manager.
    """

    name = "sysv"
    binary = "service"

    @staticmethod
    def detect(runner) -> bool:
        """Check if SysV service command is available."""
        exit_code, _, _ = runner.run_command_with_status("which service")
        return exit_code == 0

    @staticmethod
    def get_service_status(runner, service_name: str) -> ServiceStatus:
        """Get service status from SysV init."""
        status = ServiceStatus(service_manager="sysv")

        # Check if service exists
        exit_code, stdout, _ = runner.run_command_with_status(
            f"service {service_name} status"
        )

        status.exists = exit_code != 127  # 127 = command not found

        if not status.exists:
            status.error = f"Service '{service_name}' does not exist"
            return status

        # Check if running based on status output
        status.running = "running" in stdout.lower() and exit_code == 0
        status.state = "active" if status.running else "inactive"
        status.raw_status = stdout

        # Check if enabled (check runlevels)
        exit_code, _, _ = runner.run_command_with_status("ls /etc/init.d")
        if exit_code == 0:
            for i in range(2, 6):  # Check runlevels 2-5
                exit_code, stdout, _ = runner.run_command_with_status(
                    f"ls /etc/rc{i}.d/S*{service_name} 2>/dev/null || "
                    f"ls /etc/rc.d/rc{i}.d/S*{service_name} 2>/dev/null"
                )
                if exit_code == 0 and stdout.strip():
                    status.enabled = True
                    break

        return status


class OpenRCManager:
    """
    OpenRC service manager (Alpine, Gentoo).
    """

    name = "openrc"
    binary = "rc-service"

    @staticmethod
    def detect(runner) -> bool:
        """Check if OpenRC is available."""
        exit_code, _, _ = runner.run_command_with_status("which rc-service")
        return exit_code == 0

    @staticmethod
    def get_service_status(runner, service_name: str) -> ServiceStatus:
        """Get service status from OpenRC."""
        status = ServiceStatus(service_manager="openrc")

        # Check if service exists and is running
        exit_code, stdout, _ = runner.run_command_with_status(
            f"rc-service {service_name} status"
        )

        status.exists = exit_code != 127
        if not status.exists:
            status.error = f"Service '{service_name}' does not exist"
            return status

        status.running = "started" in stdout.lower()
        status.state = "active" if status.running else "inactive"
        status.raw_status = stdout

        # Check if enabled
        exit_code, stdout, _ = runner.run_command_with_status("rc-update show")
        status.enabled = service_name in stdout

        return status


# Registry of service managers (ordered by priority)
SERVICE_MANAGERS = [SystemdManager, OpenRCManager, SysVManager]


def get_service_status(runner, service_name: str) -> ServiceStatus:
    """
    Get service status using the first available service manager.

    Args:
        runner: Runner instance
        service_name: Name of the service

    Returns:
        ServiceStatus object
    """
    for manager_class in SERVICE_MANAGERS:
        if manager_class.detect(runner):
            logger.debug(f"Using {manager_class.name} service manager")
            return manager_class.get_service_status(runner, service_name)

    # No service manager found
    logger.warning("No supported service manager found")
    return ServiceStatus(
        error="No supported service manager found (systemd, sysv, openrc)"
    )
