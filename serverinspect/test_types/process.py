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
    - process: Name of the process to check
    - running: Whether the process should be running
    - count: Number of process instances expected
    
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
    if 'process' not in test_config:
        raise ValueError("Process test requires 'process' parameter")
    
    process_name = test_config['process']
    result['details']['process'] = process_name
    
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
    if 'count' in test_config:
        expected_count = test_config['count']
        result['details']['expected_count'] = expected_count
        
        if process_info['count'] != expected_count:
            result['result'] = False
            result['details']['error'] = f"Expected {expected_count} instance(s) of '{process_name}', found {process_info['count']}"
    
    return result
