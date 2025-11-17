"""
Pytest configuration and shared fixtures
"""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Sample test configuration."""
    return {
        "title": "Test Configuration",
        "description": "A test configuration for unit tests",
        "tests": [
            {
                "name": "Test File Exists",
                "type": "file",
                "path": "/etc/hosts",
                "exists": True
            },
            {
                "name": "Test Command",
                "type": "command",
                "command": "echo test",
                "exit_status": 0
            }
        ]
    }


@pytest.fixture
def sample_yaml_config(temp_dir):
    """Create a sample YAML config file."""
    import yaml
    
    config = {
        "title": "Sample Test",
        "tests": [
            {
                "name": "Echo test",
                "type": "command",
                "command": "echo hello",
                "exit_status": 0
            }
        ]
    }
    
    config_file = temp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    
    return config_file


@pytest.fixture
def mock_command_output():
    """Mock command execution output."""
    class MockResult:
        def __init__(self, stdout="", stderr="", exit_code=0):
            self.stdout = stdout
            self.stderr = stderr
            self.exit_code = exit_code
    
    return MockResult
