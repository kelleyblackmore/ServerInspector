"""
Service test type for ServerInspect.
"""
import logging
from serverinspect.test_types.base import run_test

logger = logging.getLogger("serverinspect")

def run(runner, test_config):
    """
    Run a service test.
    
    Args:
        runner: A runner instance
        test_config (dict): Test configuration
        
    Returns:
        dict: Test result
    """
    return run_test(runner, test_config, _run_service_test)

def _run_service_test(runner, test_config):
    """
    Execute a service test.
    
    Supported test options:
    - service: Name of the service
    - running: Whether the service should be running
    - enabled: Whether the service should be enabled to start on boot
    
    Args:
        runner: A runner instance
        test_config (dict): Test configuration
        
    Returns:
        dict: Test result
    """
    result = {
        'result': True,
        'details': {}
    }
    
    # Required parameters
    if 'service' not in test_config:
        raise ValueError("Service test requires 'service' parameter")
    
    service_name = test_config['service']
    result['details']['service'] = service_name
    
    # Get service status
    service_info = runner.service_status(service_name)
    result['details'].update(service_info)
    
    # Check if the service exists
    if not service_info['exists']:
        result['result'] = False
        result['details']['error'] = f"Service '{service_name}' does not exist"
        return result
    
    # Check if the service is running
    if 'running' in test_config:
        expected_running = test_config['running']
        result['details']['expected_running'] = expected_running
        
        if service_info['running'] != expected_running:
            result['result'] = False
            if expected_running:
                result['details']['error'] = f"Service '{service_name}' is not running"
            else:
                result['details']['error'] = f"Service '{service_name}' is running but should not be"
    
    # Check if the service is enabled
    if 'enabled' in test_config:
        expected_enabled = test_config['enabled']
        result['details']['expected_enabled'] = expected_enabled
        
        if service_info['enabled'] != expected_enabled:
            result['result'] = False
            if expected_enabled:
                result['details']['error'] = f"Service '{service_name}' is not enabled"
            else:
                result['details']['error'] = f"Service '{service_name}' is enabled but should not be"
    
    return result
