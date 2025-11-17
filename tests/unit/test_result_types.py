"""
Unit tests for result types and data structures
"""

from serverinspector.result_types import (
    ErrorCode,
    FileCheckResult,
    ResultStatus,
    TestResult,
)


class TestResultStatus:
    """Test ResultStatus enum."""

    def test_result_status_values(self):
        """Test that ResultStatus has expected values."""
        assert ResultStatus.PASS.value == "pass"
        assert ResultStatus.FAIL.value == "fail"
        assert ResultStatus.ERROR.value == "error"
        assert ResultStatus.SKIP.value == "skip"


class TestTestResult:
    """Test TestResult dataclass."""

    def test_create_passing_result(self):
        """Test creating a passing test result."""
        result = TestResult(
            name="Test",
            test_type="command",
            status=ResultStatus.PASS,
            message="Command executed successfully",
            details={"exit_code": 0},
        )

        assert result.success
        assert not result.failed
        assert result.name == "Test"
        assert result.test_type == "command"

    def test_create_failing_result(self):
        """Test creating a failing test result."""
        result = TestResult(
            name="Failed Test",
            test_type="file",
            status=ResultStatus.FAIL,
            message="File does not exist",
            error_code=ErrorCode.FILE_NOT_FOUND,
            details={"path": "/nonexistent"},
        )

        assert result.failed
        assert not result.success
        assert result.error_code == ErrorCode.FILE_NOT_FOUND

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = TestResult(
            name="Value Check",
            test_type="command",
            status=ResultStatus.FAIL,
            message="Values don't match",
        )

        result_dict = result.to_dict()
        assert result_dict["name"] == "Value Check"
        assert result_dict["type"] == "command"
        assert result_dict["status"] == "fail"


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_error_code_categories(self):
        """Test that error codes are properly categorized."""
        # File errors (10-19)
        assert 10 <= ErrorCode.FILE_NOT_FOUND.value <= 19
        assert 10 <= ErrorCode.FILE_EXISTS.value <= 19

        # Service errors (20-29)
        assert 20 <= ErrorCode.SERVICE_NOT_FOUND.value <= 29
        assert 20 <= ErrorCode.SERVICE_NOT_RUNNING.value <= 29

        # Package errors (30-39)
        assert 30 <= ErrorCode.PACKAGE_NOT_INSTALLED.value <= 39

        # Command errors (40-49)
        assert 40 <= ErrorCode.COMMAND_NOT_FOUND.value <= 49
        assert 40 <= ErrorCode.EXIT_CODE_MISMATCH.value <= 49

        # Process errors (50-59)
        assert 50 <= ErrorCode.PROCESS_NOT_RUNNING.value <= 59

        # Network/Port errors (60-69)
        assert 60 <= ErrorCode.PORT_NOT_LISTENING.value <= 69


class TestFileCheckResult:
    """Test FileCheckResult helper class."""

    def test_create_not_found_result(self):
        """Test creating a file not found result."""
        result = FileCheckResult.not_found(
            name="Missing File", path="/nonexistent/file.txt"
        )

        assert result.status == ResultStatus.FAIL
        assert result.error_code == ErrorCode.FILE_NOT_FOUND
        assert result.details["path"] == "/nonexistent/file.txt"
        assert len(result.suggestions) > 0

    def test_add_suggestion(self):
        """Test adding suggestions to results."""
        result = TestResult(
            name="Test",
            test_type="file",
            status=ResultStatus.FAIL,
            message="Test failed",
        )

        result.add_suggestion("Check file permissions")
        result.add_suggestion("Verify path exists")

        assert len(result.suggestions) == 2
        assert "permissions" in result.suggestions[0]

    def test_add_metadata(self):
        """Test adding metadata to results."""
        result = TestResult(
            name="Test",
            test_type="command",
            status=ResultStatus.PASS,
            message="Success",
        )

        result.add_metadata("duration", 1.5)
        result.add_metadata("retries", 0)

        assert result.metadata["duration"] == 1.5
        assert result.metadata["retries"] == 0
