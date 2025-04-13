"""
Process test type for ServerInspect.
"""
import logging
from serverinspect.test_types.base import run_test

logger = logging.getLogger("serverinspect")

def run(runner, test_config):
    """
    Run a process test.
    
    Args:
        runner: A runner instance
        test_config (dict): Test configuration
        
    Returns:
        dict: Test result
    """
    return run_test(runner, test_config, _run_process_test)

def _run_process_test(runner, test_config):
    """
    Execute a process test.
    
    Supported test options:
    - process_name: Name of the process to check
    - running: Whether the process should be running
    - min_count: Minimum number of process instances expected
    - max_count: Maximum number of process instances expected
    - user: User running the process
    
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
    if 'process_name' not in test_config and 'process' not in test_config:
        raise ValueError("Process test requires 'process_name' parameter")
    
    # Support both process_name and process for backward compatibility
    process_name = test_config.get('process_name', test_config.get('process'))
    result['details']['process_name'] = process_name
    
    # Get process status
    process_info = runner.process_status(process_name)
    result['details'].update(process_info)
    
    # Check if the process is running
    if 'running' in test_config:
        expected_running = test_config['running']
        result['details']['expected_running'] = expected_running
        
        if process_info['running'] != expected_running:
            result['result'] = False
            if expected_running:
                result['details']['error'] = f"Process '{process_name}' is not running"
            else:
                result['details']['error'] = f"Process '{process_name}' is running but should not be"
    
    # Check process count
    if 'min_count' in test_config:
        min_count = test_config['min_count']
        result['details']['min_count'] = min_count
        
        if process_info['count'] < min_count:
            result['result'] = False
            result['details']['error'] = f"Expected at least {min_count} instance(s) of '{process_name}', found {process_info['count']}"
    
    if 'max_count' in test_config:
        max_count = test_config['max_count']
        result['details']['max_count'] = max_count
        
        if process_info['count'] > max_count:
            result['result'] = False
            result['details']['error'] = f"Expected at most {max_count} instance(s) of '{process_name}', found {process_info['count']}"
    
    # Check process user
    if 'user' in test_config and process_info['running']:
        expected_user = test_config['user']
        result['details']['expected_user'] = expected_user
        
        # Get the actual user
        cmd = f"ps -o user= -p $(pgrep -f '{process_name}' | head -1)"
        actual_user = runner.run_command(cmd).strip()
        result['details']['actual_user'] = actual_user
        
        if actual_user != expected_user:
            result['result'] = False
            result['details']['error'] = f"Process '{process_name}' is running as '{actual_user}', expected '{expected_user}'"
    
    return result
