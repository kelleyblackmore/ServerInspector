"""
Unit tests for runner modules
"""

from unittest.mock import Mock, patch

from serverinspector.runners import get_runner
from serverinspector.runners.local import LocalRunner


class TestGetRunner:
    """Test the get_runner factory function."""

    def test_get_local_runner(self):
        """Test getting a local runner when no host is specified."""
        runner = get_runner()

        assert isinstance(runner, LocalRunner)

    def test_get_local_runner_explicit_none(self):
        """Test getting a local runner with explicit None host."""
        runner = get_runner(host=None)

        assert isinstance(runner, LocalRunner)

    @patch("serverinspector.runners.ssh.SSHRunner")
    def test_get_ssh_runner(self, mock_ssh_runner_class):
        """Test getting an SSH runner when host is specified."""
        mock_instance = Mock()
        mock_ssh_runner_class.return_value = mock_instance

        runner = get_runner(
            host="example.com",
            port=2222,
            username="testuser",
            key_file="/path/to/key",
            password="testpass",
        )

        mock_ssh_runner_class.assert_called_once_with(
            "example.com", "testuser", "/path/to/key", "testpass", 2222
        )
        assert runner == mock_instance


class TestLocalRunner:
    """Test LocalRunner functionality."""

    def test_local_runner_initialization(self):
        """Test LocalRunner initialization."""
        runner = LocalRunner()

        assert runner is not None

    @patch("subprocess.run")
    def test_run_command_success(self, mock_subprocess):
        """Test successful local command execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        runner = LocalRunner()
        stdout = runner.run_command("echo test")

        assert stdout == "output"

    @patch("subprocess.run")
    def test_run_command_with_status(self, mock_subprocess):
        """Test command execution with status."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        runner = LocalRunner()
        exit_code, stdout, stderr = runner.run_command_with_status("echo test")

        assert exit_code == 0
        assert stdout == "output"
        assert stderr == ""

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_subprocess):
        """Test failed local command execution."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error message"
        mock_subprocess.return_value = mock_result

        runner = LocalRunner()
        exit_code, stdout, stderr = runner.run_command_with_status("false")

        assert exit_code == 1
        assert stderr == "error message"

    def test_file_exists(self):
        """Test file existence check."""
        runner = LocalRunner()
        # Test with a file that definitely exists
        assert runner.file_exists("/") is True

    def test_cleanup(self):
        """Test runner cleanup doesn't raise errors."""
        runner = LocalRunner()
        if hasattr(runner, "cleanup"):
            runner.cleanup()  # Should not raise any exceptions
