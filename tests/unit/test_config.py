"""
Unit tests for configuration loading and validation
"""
import pytest
import yaml

from serverinspect.config import load_config, process_variables


class TestConfigLoading:
    """Test configuration file loading."""
    
    def test_load_valid_config(self, sample_yaml_config):
        """Test loading a valid configuration file."""
        config = load_config(str(sample_yaml_config))
        
        assert config is not None
        assert "title" in config
        assert "tests" in config
        assert len(config["tests"]) == 1
    
    def test_load_nonexistent_file(self):
        """Test loading a non-existent configuration file."""
        with pytest.raises(ValueError, match="Failed to load configuration file"):
            load_config("/nonexistent/file.yaml")
    
    def test_config_must_have_tests(self, temp_dir):
        """Test that config must have 'tests' or 'checks' section."""
        config_file = temp_dir / "invalid.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"title": "No tests"}, f)
        
        with pytest.raises(ValueError, match="must contain a 'tests' or 'checks' section"):
            load_config(str(config_file))
    
    def test_config_backward_compatibility_checks(self, temp_dir):
        """Test backward compatibility with 'checks' instead of 'tests'."""
        config_file = temp_dir / "legacy.yaml"
        config_data = {
            "title": "Legacy Config",
            "checks": [
                {"name": "Test", "type": "command", "command": "echo test", "exit_status": 0}
            ]
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        config = load_config(str(config_file))
        
        assert "tests" in config
        assert len(config["tests"]) == 1
    
    def test_tests_must_be_list(self, temp_dir):
        """Test that 'tests' must be a list."""
        config_file = temp_dir / "invalid_tests.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"tests": "not a list"}, f)
        
        with pytest.raises(ValueError, match="must be a list"):
            load_config(str(config_file))
    
    def test_test_must_have_name(self, temp_dir):
        """Test that each test must have a name."""
        config_file = temp_dir / "no_name.yaml"
        config_data = {
            "tests": [
                {"type": "command", "command": "echo test"}
            ]
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        with pytest.raises(ValueError, match="must have a 'name'"):
            load_config(str(config_file))
    
    def test_test_must_have_type(self, temp_dir):
        """Test that each test must have a type."""
        config_file = temp_dir / "no_type.yaml"
        config_data = {
            "tests": [
                {"name": "Test", "command": "echo test"}
            ]
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        with pytest.raises(ValueError, match="must have a 'type'"):
            load_config(str(config_file))


class TestVariableProcessing:
    """Test variable substitution in configurations."""
    
    def test_simple_variable_substitution(self):
        """Test basic variable substitution."""
        config = {
            "tests": [
                {"name": "Test {{ var }}", "type": "command", "command": "echo {{ var }}"}
            ]
        }
        variables = {"var": "hello"}
        
        result = process_variables(config, variables)
        
        assert "hello" in result["tests"][0]["name"]
        assert "hello" in result["tests"][0]["command"]
    
    def test_multiple_variable_substitution(self):
        """Test multiple variable substitutions."""
        config = {
            "tests": [
                {
                    "name": "{{ test_name }}",
                    "type": "command",
                    "command": "{{ cmd }} {{ arg }}"
                }
            ]
        }
        variables = {
            "test_name": "Echo Test",
            "cmd": "echo",
            "arg": "world"
        }
        
        result = process_variables(config, variables)
        
        assert result["tests"][0]["name"] == "Echo Test"
        assert "echo" in result["tests"][0]["command"]
        assert "world" in result["tests"][0]["command"]
    
    def test_variable_with_spaces(self):
        """Test variable substitution with whitespace."""
        config = {"value": "{{  var  }}"}
        variables = {"var": "test"}
        
        result = process_variables(config, variables)
        
        assert result["value"] == "test"
    
    def test_numeric_variable_substitution(self):
        """Test variable substitution with numeric values."""
        config = {"port": "{{ port_num }}"}
        variables = {"port_num": 8080}
        
        result = process_variables(config, variables)
        
        assert "8080" in str(result["port"])
