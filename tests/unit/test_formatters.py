"""
Unit tests for formatter modules
"""
import pytest
import json
import yaml

from serverinspect.formatters import get_formatter
from serverinspect.formatters.json_formatter import JSONFormatter
from serverinspect.formatters.yaml_formatter import YAMLFormatter
from serverinspect.formatters.terminal_formatter import TerminalFormatter


class TestGetFormatter:
    """Test the get_formatter factory function."""
    
    def test_get_json_formatter(self):
        """Test getting JSON formatter."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)
    
    def test_get_yaml_formatter(self):
        """Test getting YAML formatter."""
        formatter = get_formatter("yaml")
        assert isinstance(formatter, YAMLFormatter)
    
    def test_get_terminal_formatter(self):
        """Test getting terminal formatter."""
        formatter = get_formatter("terminal")
        assert isinstance(formatter, TerminalFormatter)
    
    def test_unsupported_format(self):
        """Test requesting an unsupported formatter."""
        with pytest.raises(ValueError, match="Unsupported format"):
            get_formatter("unsupported")


class TestJSONFormatter:
    """Test JSON formatter."""
    
    def test_format_basic_results(self):
        """Test formatting basic results to JSON."""
        formatter = JSONFormatter()
        results = {
            "timestamp": "2025-11-17T12:00:00",
            "host": "localhost",
            "summary": {"total": 2, "passed": 1, "failed": 1},
            "tests": [
                {"name": "Test 1", "result": True},
                {"name": "Test 2", "result": False}
            ]
        }
        
        output = formatter.format(results)
        
        # Verify it's valid JSON
        parsed = json.loads(output)
        assert parsed["host"] == "localhost"
        assert parsed["summary"]["total"] == 2
        assert len(parsed["tests"]) == 2
    
    def test_format_with_system_info(self):
        """Test formatting results with system info."""
        formatter = JSONFormatter()
        results = {
            "timestamp": "2025-11-17T12:00:00",
            "host": "testhost",
            "summary": {"total": 1, "passed": 1, "failed": 0},
            "system_info": {
                "hostname": "testhost",
                "platform": "Linux"
            },
            "tests": [{"name": "Test", "result": True}]
        }
        
        output = formatter.format(results)
        parsed = json.loads(output)
        
        assert "system_info" in parsed
        assert parsed["system_info"]["hostname"] == "testhost"


class TestYAMLFormatter:
    """Test YAML formatter."""
    
    def test_format_basic_results(self):
        """Test formatting basic results to YAML."""
        formatter = YAMLFormatter()
        results = {
            "timestamp": "2025-11-17T12:00:00",
            "host": "localhost",
            "summary": {"total": 1, "passed": 1, "failed": 0},
            "tests": [{"name": "Test", "result": True}]
        }
        
        output = formatter.format(results)
        
        # Verify it's valid YAML
        parsed = yaml.safe_load(output)
        assert parsed["host"] == "localhost"
        assert parsed["summary"]["passed"] == 1
    
    def test_format_preserves_data_types(self):
        """Test that YAML formatting preserves data types."""
        formatter = YAMLFormatter()
        results = {
            "timestamp": "2025-11-17T12:00:00",
            "host": "localhost",
            "summary": {"total": 5, "passed": 3, "failed": 2},
            "tests": []
        }
        
        output = formatter.format(results)
        parsed = yaml.safe_load(output)
        
        # Verify integers stay as integers
        assert isinstance(parsed["summary"]["total"], int)
        assert isinstance(parsed["summary"]["passed"], int)


class TestTerminalFormatter:
    """Test Terminal formatter."""
    
    def test_format_creates_output(self):
        """Test that terminal formatter creates output."""
        formatter = TerminalFormatter()
        results = {
            "title": "Test Suite",
            "timestamp": "2025-11-17T12:00:00",
            "host": "localhost",
            "summary": {"total": 2, "passed": 1, "failed": 1},
            "tests": [
                {"name": "Passing Test", "result": True, "type": "command"},
                {"name": "Failing Test", "result": False, "type": "file", "error": "Not found"}
            ]
        }
        
        # Terminal formatter prints to console and returns empty string
        output = formatter.format(results)
        
        # Just verify it doesn't crash
        assert output is not None
    
    def test_format_with_system_info(self):
        """Test terminal output with system information."""
        formatter = TerminalFormatter()
        results = {
            "title": "System Test",
            "timestamp": "2025-11-17T12:00:00",
            "host": "testserver",
            "summary": {"total": 1, "passed": 1, "failed": 0},
            "system_info": {
                "hostname": "testserver",
                "platform": "Linux",
                "cpu_count": 4
            },
            "tests": [{"name": "Test", "result": True, "type": "command"}]
        }
        
        # Terminal formatter prints to console
        output = formatter.format(results)
        
        # Just verify it doesn't crash
        assert output is not None
