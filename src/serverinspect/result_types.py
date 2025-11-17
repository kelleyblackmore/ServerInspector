"""
Result types and error handling for ServerInspect.

This module provides structured result objects with proper error codes
and rich metadata for better debugging and reporting.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("serverinspect")


class ResultStatus(Enum):
    """Test result status enumeration."""

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIP = "skip"
    WARN = "warn"


class ErrorCode(Enum):
    """Standard error codes for test failures."""

    # General errors
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    INVALID_PARAMETERS = 2
    NOT_IMPLEMENTED = 3

    # File errors (10-19)
    FILE_NOT_FOUND = 10
    FILE_EXISTS = 11
    PERMISSION_DENIED = 12
    INVALID_FILE_TYPE = 13
    CONTENT_MISMATCH = 14

    # Service errors (20-29)
    SERVICE_NOT_FOUND = 20
    SERVICE_NOT_RUNNING = 21
    SERVICE_RUNNING = 22
    SERVICE_NOT_ENABLED = 23
    SERVICE_ENABLED = 24
    SERVICE_MASKED = 25

    # Package errors (30-39)
    PACKAGE_NOT_INSTALLED = 30
    PACKAGE_INSTALLED = 31
    VERSION_MISMATCH = 32
    PACKAGE_MANAGER_NOT_FOUND = 33

    # Command errors (40-49)
    COMMAND_NOT_FOUND = 40
    EXIT_CODE_MISMATCH = 41
    OUTPUT_MISMATCH = 42
    COMMAND_TIMEOUT = 43

    # Process errors (50-59)
    PROCESS_NOT_RUNNING = 50
    PROCESS_RUNNING = 51
    PROCESS_COUNT_MISMATCH = 52

    # Network/Port errors (60-69)
    PORT_NOT_LISTENING = 60
    PORT_LISTENING = 61
    CONNECTION_FAILED = 62


@dataclass
class TestResult:
    """
    Structured test result with rich metadata.
    """

    name: str
    test_type: str
    status: ResultStatus
    message: str = ""
    error_code: ErrorCode = ErrorCode.SUCCESS
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if test was successful."""
        return self.status == ResultStatus.PASS

    @property
    def failed(self) -> bool:
        """Check if test failed."""
        return self.status == ResultStatus.FAIL

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type": self.test_type,
            "status": self.status.value,
            "success": self.success,
            "message": self.message,
            "error_code": self.error_code.value,
            "details": self.details,
            "metadata": self.metadata,
            "suggestions": self.suggestions,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
        }

    def add_suggestion(self, suggestion: str):
        """Add a troubleshooting suggestion."""
        self.suggestions.append(suggestion)

    def add_metadata(self, key: str, value: Any):
        """Add metadata."""
        self.metadata[key] = value


@dataclass
class FileCheckResult(TestResult):
    """File-specific test result with additional helpers."""

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, test_type="file", **kwargs)

    @classmethod
    def not_found(cls, name: str, path: str) -> "FileCheckResult":
        """Create result for file not found."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"File '{path}' does not exist",
            error_code=ErrorCode.FILE_NOT_FOUND,
        )
        result.details["path"] = path
        result.details["exists"] = False
        result.add_suggestion(f"Create the file: touch {path}")
        result.add_suggestion(f"Check if path is correct: ls -la {path}")
        return result

    @classmethod
    def permission_mismatch(
        cls, name: str, path: str, expected: str, actual: str
    ) -> "FileCheckResult":
        """Create result for permission mismatch."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"File '{path}' has permissions {actual}, expected {expected}",
            error_code=ErrorCode.PERMISSION_DENIED,
        )
        result.details["path"] = path
        result.details["expected_permissions"] = expected
        result.details["actual_permissions"] = actual
        result.add_suggestion(f"Fix permissions: chmod {expected} {path}")
        return result


@dataclass
class ServiceCheckResult(TestResult):
    """Service-specific test result with additional helpers."""

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, test_type="service", **kwargs)

    @classmethod
    def not_found(cls, name: str, service_name: str) -> "ServiceCheckResult":
        """Create result for service not found."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"Service '{service_name}' does not exist",
            error_code=ErrorCode.SERVICE_NOT_FOUND,
        )
        result.details["service"] = service_name
        result.details["exists"] = False
        result.add_suggestion(
            f"Install the service package for '{service_name}'"
        )
        result.add_suggestion(
            f"Check service name: systemctl list-unit-files | grep {service_name}"
        )
        return result

    @classmethod
    def not_running(
        cls, name: str, service_name: str, state: str = None
    ) -> "ServiceCheckResult":
        """Create result for service not running."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"Service '{service_name}' is not running",
            error_code=ErrorCode.SERVICE_NOT_RUNNING,
        )
        result.details["service"] = service_name
        result.details["running"] = False
        if state:
            result.details["state"] = state
            result.message += f" (state: {state})"
        result.add_suggestion(f"Start the service: systemctl start {service_name}")
        result.add_suggestion(f"Check logs: journalctl -u {service_name} -n 50")
        return result


@dataclass
class PackageCheckResult(TestResult):
    """Package-specific test result with additional helpers."""

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, test_type="package", **kwargs)

    @classmethod
    def not_installed(cls, name: str, package_name: str) -> "PackageCheckResult":
        """Create result for package not installed."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"Package '{package_name}' is not installed",
            error_code=ErrorCode.PACKAGE_NOT_INSTALLED,
        )
        result.details["package"] = package_name
        result.details["installed"] = False
        result.add_suggestion(f"Install package: apt install {package_name}")
        result.add_suggestion(f"Or with yum: yum install {package_name}")
        return result

    @classmethod
    def version_mismatch(
        cls, name: str, package_name: str, expected: str, actual: str
    ) -> "PackageCheckResult":
        """Create result for version mismatch."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"Package '{package_name}' version is {actual}, expected {expected}",
            error_code=ErrorCode.VERSION_MISMATCH,
        )
        result.details["package"] = package_name
        result.details["expected_version"] = expected
        result.details["actual_version"] = actual
        result.add_suggestion(f"Update package to version {expected}")
        return result


@dataclass
class CommandCheckResult(TestResult):
    """Command-specific test result with additional helpers."""

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, test_type="command", **kwargs)

    @classmethod
    def exit_code_mismatch(
        cls, name: str, command: str, expected: int, actual: int, stderr: str = ""
    ) -> "CommandCheckResult":
        """Create result for exit code mismatch."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"Command '{command}' exited with {actual}, expected {expected}",
            error_code=ErrorCode.EXIT_CODE_MISMATCH,
        )
        result.details["command"] = command
        result.details["expected_exit_code"] = expected
        result.details["actual_exit_code"] = actual
        if stderr:
            result.details["stderr"] = stderr
            result.add_suggestion(f"Check error output: {stderr[:100]}")
        return result


@dataclass
class ProcessCheckResult(TestResult):
    """Process-specific test result with additional helpers."""

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, test_type="process", **kwargs)

    @classmethod
    def not_running(cls, name: str, process_name: str) -> "ProcessCheckResult":
        """Create result for process not running."""
        result = cls(
            name=name,
            status=ResultStatus.FAIL,
            message=f"Process '{process_name}' is not running",
            error_code=ErrorCode.PROCESS_NOT_RUNNING,
        )
        result.details["process_name"] = process_name
        result.details["running"] = False
        result.details["count"] = 0
        result.add_suggestion(f"Start the process/service")
        result.add_suggestion(f"Check with: ps aux | grep {process_name}")
        return result


class ResultBuilder:
    """
    Builder for creating test results with proper error handling.
    """

    @staticmethod
    def success(name: str, test_type: str, message: str = "", **kwargs) -> TestResult:
        """Create a successful test result."""
        return TestResult(
            name=name,
            test_type=test_type,
            status=ResultStatus.PASS,
            message=message or f"{test_type} check passed",
            error_code=ErrorCode.SUCCESS,
            **kwargs,
        )

    @staticmethod
    def failure(
        name: str,
        test_type: str,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        **kwargs,
    ) -> TestResult:
        """Create a failed test result."""
        return TestResult(
            name=name,
            test_type=test_type,
            status=ResultStatus.FAIL,
            message=message,
            error_code=error_code,
            **kwargs,
        )

    @staticmethod
    def error(
        name: str, test_type: str, error_message: str, **kwargs
    ) -> TestResult:
        """Create an error test result."""
        return TestResult(
            name=name,
            test_type=test_type,
            status=ResultStatus.ERROR,
            message=f"Error during test execution: {error_message}",
            error_code=ErrorCode.UNKNOWN_ERROR,
            **kwargs,
        )
