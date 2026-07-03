"""
Configuration loading and validation for serverinspector.
"""

import logging
import re
from pathlib import Path

import yaml

logger = logging.getLogger("serverinspector")


def load_config(config_path):
    """
    Load and validate a configuration file.

    Args:
        config_path (str): Path to the YAML configuration file

    Returns:
        dict: The validated configuration

    Raises:
        ValueError: If the configuration is invalid
    """
    logger.debug(f"Loading configuration from {config_path}")

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load configuration file: {str(e)}")

    # Validate basic structure
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML dictionary")

    # Check for tests or legacy tests section
    if "tests" not in config and "checks" not in config:
        raise ValueError("Configuration must contain a 'tests' or 'checks' section")

    # For backward compatibility, use 'checks' if 'tests' is not present
    if "tests" not in config and "checks" in config:
        config["tests"] = config["checks"]

    if not isinstance(config["tests"], list):
        raise ValueError("The 'tests' section must be a list")

    # Process environment variables if defined
    variables = {}
    if "environment" in config and "variables" in config["environment"]:
        variables = config["environment"]["variables"]
        logger.debug(
            f"Loaded {len(variables)} environment variables from configuration"
        )

    # Apply variable substitution
    if variables:
        config = process_variables(config, variables)

    # Validate each test
    for i, test in enumerate(config["tests"]):
        if not isinstance(test, dict):
            raise ValueError(f"Test {i+1} must be a dictionary")

        if "name" not in test:
            raise ValueError(f"Test {i+1} must have a 'name'")

        if "type" not in test:
            raise ValueError(f"Test '{test['name']}' must have a 'type'")

    logger.debug(f"Loaded {len(config['tests'])} tests from configuration")
    return config


def process_variables(config, variables):
    """
    Process variable substitution in the configuration.

    Args:
        config (dict): The configuration dictionary
        variables (dict): The environment variables

    Returns:
        dict: The configuration with variables substituted
    """
    # Substitute directly on the structure rather than a YAML dump so that
    # values containing backslashes (e.g. Windows paths) or YAML syntax
    # cannot corrupt the document or be misread as regex escapes.
    patterns = {
        var_name: re.compile(r"\{\{\s*" + re.escape(var_name) + r"\s*\}\}")
        for var_name in variables
    }

    def substitute(value):
        if isinstance(value, str):
            for var_name, pattern in patterns.items():
                var_value = variables[var_name]
                # A string that is exactly one variable reference keeps the
                # variable's original type (int, bool, ...)
                if pattern.fullmatch(value):
                    return var_value
                value = pattern.sub(lambda _m, v=var_value: str(v), value)
            return value
        if isinstance(value, dict):
            return {substitute(k): substitute(v) for k, v in value.items()}
        if isinstance(value, list):
            return [substitute(item) for item in value]
        return value

    return substitute(config)


def get_default_config_path():
    """
    Returns the default configuration path.

    Returns:
        Path: The default configuration path
    """
    # Look in several places
    # 1. Current directory
    # 2. User home directory
    # 3. System config directory

    possible_paths = [
        Path.cwd() / "serverinspector.yaml",
        Path.cwd() / "serverinspector.yml",
        Path.home() / ".serverinspector.yaml",
        Path.home() / ".serverinspector.yml",
        Path("/etc/serverinspector/config.yaml"),
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None
