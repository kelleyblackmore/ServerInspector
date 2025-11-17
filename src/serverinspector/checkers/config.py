"""
Configuration file checker module for serverinspector.

This module provides functions to check configuration files by parsing their content
and validating settings against expected values.
"""

import configparser
import json
import logging
import os
import re

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger("serverinspector")


def _parse_config_file(file_path, file_format=None):
    """
    Parse a configuration file based on its format.

    Args:
        file_path (str): Path to the configuration file
        file_format (str, optional): Format of the file ('ini', 'json', 'yaml')
                                     If not provided, will be guessed from extension

    Returns:
        tuple: (parsed_config, format_used)

    Raises:
        ValueError: If the file format is not supported or cannot be determined
        Exception: Any other parsing errors
    """
    if not os.path.exists(file_path):
        raise ValueError(f"Configuration file does not exist: {file_path}")

    # Determine format if not provided
    if not file_format:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext in [".ini", ".conf", ".cfg"]:
            file_format = "ini"
        elif ext in [".json"]:
            file_format = "json"
        elif ext in [".yaml", ".yml"]:
            file_format = "yaml"
        else:
            # Try to guess based on content
            with open(file_path, "r") as f:
                first_line = f.readline().strip()
                if first_line.startswith("{"):
                    file_format = "json"
                elif first_line.startswith("#") or first_line.startswith("["):
                    # Could be INI or YAML
                    file_format = "ini"  # Default to INI
                else:
                    raise ValueError(f"Could not determine format of {file_path}")

    # Parse according to format
    try:
        if file_format == "ini":
            config = configparser.ConfigParser()
            config.read(file_path)
            return config, "ini"

        elif file_format == "json":
            with open(file_path, "r") as f:
                config = json.load(f)
            return config, "json"

        elif file_format == "yaml":
            if not YAML_AVAILABLE:
                raise ValueError("YAML parsing requires PyYAML package")

            with open(file_path, "r") as f:
                config = yaml.safe_load(f)
            return config, "yaml"

        else:
            raise ValueError(f"Unsupported configuration format: {file_format}")

    except Exception as e:
        logger.error(f"Error parsing {file_format} file {file_path}: {str(e)}")
        raise


def _get_config_value(config, key_path, format_type):
    """
    Get a value from a parsed configuration using a dot-separated path.

    Args:
        config: The parsed configuration
        key_path (str): Dot-separated path to the value (e.g., "section.key")
        format_type (str): Format of the config ('ini', 'json', 'yaml')

    Returns:
        The value at the specified path, or None if not found
    """
    if format_type == "ini":
        # Handle INI format
        parts = key_path.split(".")
        if len(parts) == 1:
            # Looking for a section
            return parts[0] in config.sections()

        section, key = parts[0], ".".join(parts[1:])
        if section in config.sections() and key in config[section]:
            return config[section][key]
        return None

    else:
        # Handle hierarchical formats (JSON, YAML)
        parts = key_path.split(".")
        current = config

        for part in parts:
            # Handle array indices like "items[0]"
            match = re.match(r"(\w+)\[(\d+)\]", part)
            if match:
                name, index = match.groups()
                index = int(index)

                if (
                    name in current
                    and isinstance(current[name], list)
                    and 0 <= index < len(current[name])
                ):
                    current = current[name][index]
                else:
                    return None
            else:
                # Regular key
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None

        return current


def check(params):
    """
    Perform a configuration file check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - path: Path to the configuration file
            - format: Format of the file ('ini', 'json', 'yaml')
            - has_key: Key that should exist in the config (dot notation)
            - has_value: Dict with key-value pairs that should exist
            - compare_with: Another configuration file to compare with
            - compare_keys: List of keys to compare between files

    Returns:
        dict: Check result with success/failure and details
    """
    result = {"success": False, "message": "", "details": {}}

    # Required parameters
    if "path" not in params:
        result["message"] = "Missing required parameter: path"
        return result

    path = params["path"]
    result["details"]["path"] = path

    # Check if the file exists
    if not os.path.exists(path):
        result["message"] = f"Configuration file '{path}' does not exist"
        return result

    # Parse the configuration file
    try:
        format_type = params.get("format")
        config, detected_format = _parse_config_file(path, format_type)
        result["details"]["format"] = detected_format
    except Exception as e:
        result["message"] = f"Error parsing configuration file '{path}': {str(e)}"
        return result

    # Check for specific key
    if "has_key" in params:
        key_path = params["has_key"]
        value = _get_config_value(config, key_path, detected_format)

        if value is None:
            result["message"] = f"Key '{key_path}' not found in configuration file"
            return result

        result["details"]["found_key"] = key_path
        result["details"]["key_value"] = str(value)

    # Check for specific key-value pairs
    if "has_value" in params:
        value_checks = params["has_value"]

        if isinstance(value_checks, dict):
            # Convert to list of key-value pairs
            value_checks = [{"key": k, "value": v} for k, v in value_checks.items()]

        for check_item in value_checks:
            key_path = check_item["key"]
            expected_value = check_item["value"]

            value = _get_config_value(config, key_path, detected_format)

            if value is None:
                result["message"] = f"Key '{key_path}' not found in configuration file"
                return result

            # Convert to strings for comparison
            str_value = str(value).strip()
            str_expected = str(expected_value).strip()

            if str_value != str_expected:
                result["message"] = (
                    f"Value for '{key_path}' is '{str_value}', expected '{str_expected}'"
                )
                return result

            result["details"][f"value_match_{key_path}"] = True

    # Compare with another configuration file
    if "compare_with" in params:
        compare_path = params["compare_with"]
        result["details"]["compare_with"] = compare_path

        if not os.path.exists(compare_path):
            result["message"] = f"Comparison file '{compare_path}' does not exist"
            return result

        try:
            compare_format = params.get("compare_format")
            compare_config, compare_format = _parse_config_file(
                compare_path, compare_format
            )
            result["details"]["compare_format"] = compare_format
        except Exception as e:
            result["message"] = (
                f"Error parsing comparison file '{compare_path}': {str(e)}"
            )
            return result

        # Check specific keys to compare
        if "compare_keys" in params:
            compare_keys = params["compare_keys"]
            mismatches = []

            for key_path in compare_keys:
                value1 = _get_config_value(config, key_path, detected_format)
                value2 = _get_config_value(compare_config, key_path, compare_format)

                if value1 != value2:
                    mismatches.append(f"{key_path}: '{value1}' vs '{value2}'")

            if mismatches:
                result["message"] = (
                    f"Configuration files have {len(mismatches)} mismatched values"
                )
                result["details"]["mismatches"] = mismatches
                return result

            result["details"]["compared_keys"] = len(compare_keys)
        else:
            # Full comparison is complex because different formats might have different structures
            result["details"][
                "warning"
            ] = "Full comparison is not supported, specify compare_keys"

    # All checks passed
    result["success"] = True
    result["message"] = f"Configuration file '{path}' passed all checks"

    return result


def run(_runner, test_config):
    """
    Run a configuration file test (legacy API for backward compatibility).

    Args:
        _runner: A runner instance (unused, kept for API compatibility)
        test_config (dict): Test configuration

    Returns:
        dict: Test result in the old format
    """
    # Convert parameters to the new format
    params = {"path": test_config.get("path")}

    # Copy other parameters
    if "format" in test_config:
        params["format"] = test_config["format"]

    if "has_key" in test_config:
        params["has_key"] = test_config["has_key"]

    if "has_value" in test_config:
        params["has_value"] = test_config["has_value"]

    if "compare_with" in test_config:
        params["compare_with"] = test_config["compare_with"]

    if "compare_keys" in test_config:
        params["compare_keys"] = test_config["compare_keys"]

    # Run the check
    result = check(params)

    # Convert the result back to the old format
    old_result = {
        "name": test_config.get("name", "Unnamed config test"),
        "type": "config",
        "result": result["success"],
        "details": result["details"],
    }

    # Add error message if check failed
    if not result["success"]:
        old_result["details"]["error"] = result["message"]

    return old_result
