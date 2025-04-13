"""
Process checker module for ServerInspect.

This module provides simple functions to check process-related aspects of a system.
"""

import subprocess
import logging

logger = logging.getLogger("serverinspect")

def check(params):
    """
    Perform a process check with the given parameters.
    
    Args:
        params (dict): Check parameters, including:
            - process_name: Name of the process to check
            - running: Whether the process should be running
            
    Returns:
        dict: Check result with success/failure and details
    """
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    # Required parameters
    if 'process_name' not in params and 'process' not in params:
        result['message'] = "Missing required parameter: process_name"
        return result
    
    # Support both process_name and process for backward compatibility
    process_name = params.get('process_name', params.get('process'))
    result['details']['process_name'] = process_name
    
    # Check if the process is running
    try:
        # Use pgrep to check if the process is running
        proc = subprocess.run(['pgrep', '-f', process_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        running = proc.returncode == 0
        result['details']['running'] = running
        
        # Get process count
        if running:
            count_proc = subprocess.run(['pgrep', '-fc', process_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            process_count = int(count_proc.stdout.strip()) if count_proc.returncode == 0 else 0
        else:
            process_count = 0
        result['details']['count'] = process_count
        
        # Check the running requirement
        if 'running' in params:
            expected_running = params['running']
            result['details']['expected_running'] = expected_running
            
            if running == expected_running:
                result['success'] = True
                if expected_running:
                    result['message'] = f"Process '{process_name}' is running as expected"
                else:
                    result['message'] = f"Process '{process_name}' is not running as expected"
            else:
                if expected_running:
                    result['message'] = f"Process '{process_name}' is not running"
                else:
                    result['message'] = f"Process '{process_name}' is running but should not be"
        else:
            # If we're not checking running status, just report it
            result['success'] = True
            result['message'] = f"Process '{process_name}' running status is {running}"
    
    except Exception as e:
        result['message'] = f"Error checking process '{process_name}': {str(e)}"
        result['details']['error'] = str(e)
    
    return result
