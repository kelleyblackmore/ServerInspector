"""
Configuration loading and validation for ServerInspect.
"""
import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger("serverinspect")

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
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load configuration file: {str(e)}")
    
    # Validate basic structure
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML dictionary")
    
    # Check for required keys
    if 'tests' not in config:
        raise ValueError("Configuration must contain a 'tests' section")
    
    if not isinstance(config['tests'], list):
        raise ValueError("The 'tests' section must be a list")
    
    # Validate each test
    for i, test in enumerate(config['tests']):
        if not isinstance(test, dict):
            raise ValueError(f"Test {i+1} must be a dictionary")
        
        if 'name' not in test:
            raise ValueError(f"Test {i+1} must have a 'name'")
        
        if 'type' not in test:
            raise ValueError(f"Test '{test['name']}' must have a 'type'")
    
    logger.debug(f"Loaded {len(config['tests'])} tests from configuration")
    return config

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
        Path.cwd() / "serverinspect.yaml",
        Path.cwd() / "serverinspect.yml",
        Path.home() / ".serverinspect.yaml",
        Path.home() / ".serverinspect.yml",
        Path("/etc/serverinspect/config.yaml"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None
