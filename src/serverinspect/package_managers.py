"""
Package manager registry for ServerInspect.

This module provides a centralized registry of package managers with their
detection, query, and version extraction logic.
"""

import logging
import re
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

logger = logging.getLogger("serverinspect")


@dataclass
class PackageManager:
    """
    Definition of a package manager with its commands and parsers.
    """

    name: str
    binary: str  # Primary binary name
    check_cmd: str  # Command template to check if package is installed
    version_cmd: Optional[str] = None  # Command to get version (if different)
    parse_version: Optional[Callable[[str], str]] = None  # Version parser function
    priority: int = 50  # Lower number = higher priority
    description: str = ""

    def detect(self, runner) -> bool:
        """
        Detect if this package manager is available.

        Args:
            runner: Runner instance with run_command_with_status method

        Returns:
            bool: True if package manager is available
        """
        exit_code, _, _ = runner.run_command_with_status(f"which {self.binary}")
        return exit_code == 0

    def check_installed(self, runner, package_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a package is installed and get its version.

        Args:
            runner: Runner instance
            package_name: Name of the package

        Returns:
            Tuple of (installed: bool, version: Optional[str])
        """
        cmd = self.check_cmd.format(package=package_name)
        exit_code, stdout, stderr = runner.run_command_with_status(cmd)

        installed = exit_code == 0
        version = None

        if installed and self.parse_version:
            version = self.parse_version(stdout)

        return installed, version


# Version parser functions
def parse_dpkg_version(output: str) -> Optional[str]:
    """Parse version from dpkg -s output."""
    for line in output.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return None


def parse_rpm_version(output: str) -> Optional[str]:
    """Parse version from rpm -q output (format: package-version-release)."""
    output = output.strip()
    # Remove package name prefix
    parts = output.split("-")
    if len(parts) >= 3:
        # Join version and release, excluding package name
        return "-".join(parts[1:])
    return output


def parse_pacman_version(output: str) -> Optional[str]:
    """Parse version from pacman -Q output (format: package version)."""
    parts = output.strip().split()
    if len(parts) >= 2:
        return parts[1]
    return None


def parse_apk_version(output: str) -> Optional[str]:
    """Parse version from apk info output."""
    for line in output.splitlines():
        match = re.search(r"(\d+[\d.\-]+)", line)
        if match:
            return match.group(1)
    return None


def parse_brew_version(output: str) -> Optional[str]:
    """Parse version from brew list --versions output."""
    parts = output.strip().split()
    if len(parts) >= 2:
        return parts[1]
    return None


def parse_pip_version(output: str) -> Optional[str]:
    """Parse version from pip show output."""
    for line in output.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return None


def parse_npm_version(output: str) -> Optional[str]:
    """Parse version from npm list output."""
    # Format: package@version
    match = re.search(r"@([\d.\-]+)", output)
    if match:
        return match.group(1)
    return None


def parse_gem_version(output: str) -> Optional[str]:
    """Parse version from gem list output."""
    # Format: package (version)
    match = re.search(r"\(([\d.\-]+)\)", output)
    if match:
        return match.group(1)
    return None


def parse_snap_version(output: str) -> Optional[str]:
    """Parse version from snap info output."""
    for line in output.splitlines():
        if line.startswith("installed:"):
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]
    return None


def parse_flatpak_version(output: str) -> Optional[str]:
    """Parse version from flatpak info output."""
    for line in output.splitlines():
        if line.strip().startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return None


def parse_zypper_version(output: str) -> Optional[str]:
    """Parse version from zypper info output."""
    for line in output.splitlines():
        if line.startswith("Version"):
            parts = line.split(":", 1)
            if len(parts) >= 2:
                return parts[1].strip()
    return None


def parse_apt_version(output: str) -> Optional[str]:
    """Parse version from apt-cache policy output."""
    for line in output.splitlines():
        if line.strip().startswith("Installed:"):
            version = line.split(":", 1)[1].strip()
            if version != "(none)":
                return version
    return None


# Package Manager Registry
PACKAGE_MANAGERS = [
    # System package managers (highest priority)
    PackageManager(
        name="apt",
        binary="apt-cache",
        check_cmd="apt-cache policy {package}",
        parse_version=parse_apt_version,
        priority=10,
        description="APT package manager (Debian, Ubuntu)",
    ),
    PackageManager(
        name="dnf",
        binary="dnf",
        check_cmd="dnf list installed {package}",
        parse_version=parse_rpm_version,
        priority=11,
        description="DNF package manager (Fedora, RHEL 8+)",
    ),
    PackageManager(
        name="yum",
        binary="yum",
        check_cmd="yum list installed {package}",
        parse_version=parse_rpm_version,
        priority=12,
        description="YUM package manager (RHEL, CentOS)",
    ),
    PackageManager(
        name="zypper",
        binary="zypper",
        check_cmd="zypper info {package}",
        parse_version=parse_zypper_version,
        priority=13,
        description="Zypper package manager (openSUSE)",
    ),
    PackageManager(
        name="apk",
        binary="apk",
        check_cmd="apk info {package}",
        parse_version=parse_apk_version,
        priority=14,
        description="APK package manager (Alpine Linux)",
    ),
    PackageManager(
        name="dpkg",
        binary="dpkg",
        check_cmd="dpkg -s {package}",
        parse_version=parse_dpkg_version,
        priority=20,
        description="DPKG low-level package manager (Debian, Ubuntu)",
    ),
    PackageManager(
        name="rpm",
        binary="rpm",
        check_cmd="rpm -q {package}",
        parse_version=parse_rpm_version,
        priority=21,
        description="RPM low-level package manager (RHEL, CentOS, Fedora)",
    ),
    PackageManager(
        name="pacman",
        binary="pacman",
        check_cmd="pacman -Q {package}",
        parse_version=parse_pacman_version,
        priority=22,
        description="Pacman package manager (Arch Linux)",
    ),
    # BSD package managers
    PackageManager(
        name="pkg",
        binary="pkg",
        check_cmd="pkg info {package}",
        parse_version=lambda x: x.splitlines()[0].split()[-1]
        if x.splitlines()
        else None,
        priority=30,
        description="PKG package manager (FreeBSD)",
    ),
    PackageManager(
        name="pkg_info",
        binary="pkg_info",
        check_cmd="pkg_info -E {package}",
        priority=31,
        description="pkg_info package manager (older FreeBSD)",
    ),
    # macOS
    PackageManager(
        name="brew",
        binary="brew",
        check_cmd="brew list --versions {package}",
        parse_version=parse_brew_version,
        priority=40,
        description="Homebrew package manager (macOS, Linux)",
    ),
    # Modern application package managers
    PackageManager(
        name="snap",
        binary="snap",
        check_cmd="snap info {package}",
        parse_version=parse_snap_version,
        priority=50,
        description="Snap package manager (Ubuntu, others)",
    ),
    PackageManager(
        name="flatpak",
        binary="flatpak",
        check_cmd="flatpak info {package}",
        parse_version=parse_flatpak_version,
        priority=51,
        description="Flatpak package manager (universal)",
    ),
    # Language-specific package managers (lowest priority)
    PackageManager(
        name="pip",
        binary="pip",
        check_cmd="pip show {package}",
        parse_version=parse_pip_version,
        priority=60,
        description="Pip package manager (Python)",
    ),
    PackageManager(
        name="pip3",
        binary="pip3",
        check_cmd="pip3 show {package}",
        parse_version=parse_pip_version,
        priority=61,
        description="Pip3 package manager (Python 3)",
    ),
    PackageManager(
        name="npm",
        binary="npm",
        check_cmd="npm list -g {package}",
        parse_version=parse_npm_version,
        priority=70,
        description="NPM package manager (Node.js)",
    ),
    PackageManager(
        name="gem",
        binary="gem",
        check_cmd="gem list {package} --installed",
        parse_version=parse_gem_version,
        priority=71,
        description="Gem package manager (Ruby)",
    ),
]


class PackageManagerRegistry:
    """
    Registry for managing package managers with caching.
    """

    def __init__(self):
        self._detected_managers = {}
        self._preferred_manager = None

    def detect_available(self, runner) -> list:
        """
        Detect all available package managers on the system.

        Args:
            runner: Runner instance

        Returns:
            List of available PackageManager instances, sorted by priority
        """
        if runner not in self._detected_managers:
            available = []
            for pm in PACKAGE_MANAGERS:
                if pm.detect(runner):
                    available.append(pm)
                    logger.debug(f"Detected package manager: {pm.name}")

            # Sort by priority (lower number = higher priority)
            available.sort(key=lambda x: x.priority)
            self._detected_managers[runner] = available

        return self._detected_managers[runner]

    def get_preferred(self, runner) -> Optional[PackageManager]:
        """
        Get the preferred (highest priority) package manager.

        Args:
            runner: Runner instance

        Returns:
            PackageManager instance or None
        """
        available = self.detect_available(runner)
        return available[0] if available else None

    def find_by_name(self, name: str) -> Optional[PackageManager]:
        """
        Find a package manager by name.

        Args:
            name: Package manager name

        Returns:
            PackageManager instance or None
        """
        for pm in PACKAGE_MANAGERS:
            if pm.name == name:
                return pm
        return None

    def check_package(
        self, runner, package_name: str, manager_name: Optional[str] = None
    ) -> dict:
        """
        Check package installation status.

        Args:
            runner: Runner instance
            package_name: Name of the package
            manager_name: Specific package manager to use (optional)

        Returns:
            dict with installed, version, package_manager keys
        """
        result = {"installed": False, "version": None, "package_manager": None}

        if manager_name:
            # Use specific package manager
            pm = self.find_by_name(manager_name)
            if pm and pm.detect(runner):
                installed, version = pm.check_installed(runner, package_name)
                result["installed"] = installed
                result["version"] = version
                result["package_manager"] = pm.name
        else:
            # Try all available package managers in priority order
            for pm in self.detect_available(runner):
                try:
                    installed, version = pm.check_installed(runner, package_name)
                    if installed:
                        result["installed"] = True
                        result["version"] = version
                        result["package_manager"] = pm.name
                        return result
                except Exception as e:
                    logger.debug(
                        f"Error checking package with {pm.name}: {str(e)}"
                    )

        return result


# Global registry instance
_registry = PackageManagerRegistry()


def get_registry() -> PackageManagerRegistry:
    """Get the global package manager registry."""
    return _registry
