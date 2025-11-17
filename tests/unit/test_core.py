"""
Unit tests for core ServerInspect functionality
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from serverinspect.core import ServerInspect


class TestServerInspectInit:
    """Test ServerInspect initialization."""

    @patch("serverinspect.core.get_runner")
    def test_init_local(self, mock_get_runner):
        """Test initialization for local execution."""
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner

        config = {"tests": []}
        inspector = ServerInspect(config=config)

        assert inspector.config == config
        assert inspector.host is None
        assert inspector.runner == mock_runner
        mock_get_runner.assert_called_once_with(None, 22, None, None, None)

    @patch("serverinspect.core.get_runner")
    def test_init_remote_ssh(self, mock_get_runner):
        """Test initialization for remote SSH execution."""
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner

        config = {"tests": []}
        inspector = ServerInspect(
            config=config,
            host="example.com",
            port=2222,
            username="testuser",
            key_file="/path/to/key",
        )

        assert inspector.host == "example.com"
        assert inspector.port == 2222
        assert inspector.username == "testuser"
        mock_get_runner.assert_called_once_with(
            "example.com", 2222, "testuser", "/path/to/key", None
        )


class TestServerInspectRunTests:
    """Test ServerInspect test execution."""

    @patch("serverinspect.core.get_runner")
    @patch("serverinspect.core.collect_system_info")
    def test_run_tests_success(self, mock_collect_info, mock_get_runner):
        """Test successful test execution."""
        # Setup mocks
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        mock_collect_info.return_value = {"hostname": "testhost"}

        # Create config and inspector
        config = {
            "title": "Test Suite",
            "tests": [
                {
                    "name": "Test 1",
                    "type": "command",
                    "command": "echo test",
                    "exit_status": 0,
                }
            ],
        }

        with patch("serverinspect.core.get_checker") as mock_get_checker:
            mock_checker_module = Mock()
            mock_checker_module.check.return_value = {"success": True, "message": "OK"}
            mock_get_checker.return_value = mock_checker_module

            inspector = ServerInspect(config=config)
            results = inspector.run_tests()

            # Verify results structure
            assert "timestamp" in results
            assert results["host"] == "localhost"
            assert results["title"] == "Test Suite"
            assert results["summary"]["total"] == 1

    @patch("serverinspect.core.get_runner")
    @patch("serverinspect.core.collect_system_info")
    def test_run_tests_with_failures(self, mock_collect_info, mock_get_runner):
        """Test execution with some failing tests."""
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        mock_collect_info.return_value = {}

        config = {
            "tests": [
                {"name": "Test 1", "type": "command", "command": "echo test"},
                {"name": "Test 2", "type": "file", "path": "/etc/hosts"},
            ]
        }

        with patch("serverinspect.core.get_checker") as mock_get_checker:
            mock_checker_module = Mock()
            # Return pass then fail
            mock_checker_module.check.side_effect = [
                {"success": True, "message": "OK"},
                {"success": False, "message": "Failed"},
            ]
            mock_get_checker.return_value = mock_checker_module

            inspector = ServerInspect(config=config)
            results = inspector.run_tests()

            assert results["summary"]["total"] == 2

    @patch("serverinspect.core.get_runner")
    def test_run_tests_no_config(self, mock_get_runner):
        """Test that run_tests raises error with no tests."""
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner

        inspector = ServerInspect(config={})

        with pytest.raises(ValueError, match="No tests defined"):
            inspector.run_tests()

    @patch("serverinspect.core.get_runner")
    @patch("serverinspect.core.collect_system_info")
    @patch("serverinspect.core.get_checker")
    def test_run_tests_handles_exceptions(
        self, mock_get_checker, mock_collect_info, mock_get_runner
    ):
        """Test that exceptions during test execution are handled."""
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        mock_collect_info.return_value = {}

        # Checker raises exception
        mock_checker = Mock()
        mock_checker.check.side_effect = Exception("Test error")
        mock_get_checker.return_value = mock_checker

        config = {"tests": [{"name": "Test", "type": "command"}]}
        inspector = ServerInspect(config=config)

        results = inspector.run_tests()

        # Should still complete, marking test as failed
        assert results["summary"]["total"] == 1
        assert results["summary"]["failed"] == 1
        assert "error" in results["tests"][0]


class TestServerInspectOutputResults:
    """Test result output functionality."""

    @patch("serverinspect.core.get_runner")
    @patch("serverinspect.core.get_formatter")
    def test_output_to_stdout(self, mock_get_formatter, mock_get_runner):
        """Test outputting results to stdout."""
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner

        mock_formatter = Mock()
        mock_formatter.format.return_value = "formatted output"
        mock_get_formatter.return_value = mock_formatter

        inspector = ServerInspect(config={"tests": []})
        results = {"tests": []}

        inspector.output_results(results, format="json")

        mock_get_formatter.assert_called_once_with("json")
        mock_formatter.format.assert_called_once_with(results)

    @patch("serverinspect.core.get_runner")
    @patch("serverinspect.core.get_formatter")
    @patch("builtins.open", create=True)
    def test_output_to_file(self, mock_open, mock_get_formatter, mock_get_runner):
        """Test outputting results to a file."""
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner

        mock_formatter = Mock()
        mock_formatter.format.return_value = "formatted output"
        mock_get_formatter.return_value = mock_formatter

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        inspector = ServerInspect(config={"tests": []})
        results = {"tests": []}

        inspector.output_results(
            results, format="json", output_file="/tmp/results.json"
        )

        mock_open.assert_called_once_with("/tmp/results.json", "w")
        mock_file.write.assert_called_once_with("formatted output")
