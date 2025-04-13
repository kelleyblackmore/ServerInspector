"""
Port checker module for ServerInspect.

This module provides simple functions to check port-related aspects of a system.
"""

import subprocess
import logging

logger = logging.getLogger("serverinspect")

def check(params):
    """
    Perform a port check with the given parameters.
    
    Args:
        params (dict): Check parameters, including:
            - port: Port number to check
            - listening: Whether the port should be listening
            - protocol: Protocol to check (tcp, udp)
            - process: Process name that should be using the port
            
    Returns:
        dict: Check result with success/failure and details
    """
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    # Required parameters
    if 'port' not in params:
        result['message'] = "Missing required parameter: port"
        return result
    
    port = params['port']
    result['details']['port'] = port
    
    # Default protocol is tcp
    protocol = params.get('protocol', 'tcp')
    result['details']['protocol'] = protocol
    
    # Check if port is listening
    try:
        # Use ss or netstat to check for listening ports
        if subprocess.run(['which', 'ss'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
            # ss is available
            proto_flag = 't' if protocol.lower() == 'tcp' else 'u'
            cmd = ['ss', f'-ln{proto_flag}', 'state', 'listening']
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            port_listening = f":{port}" in proc.stdout
        else:
            # Fall back to netstat
            proto_flag = '--tcp' if protocol.lower() == 'tcp' else '--udp'
            cmd = ['netstat', '-ln', proto_flag]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            port_listening = f":{port}" in proc.stdout
            
        result['details']['listening'] = port_listening
        
        # Check listening state if required
        if 'listening' in params:
            expected_listening = params['listening']
            result['details']['expected_listening'] = expected_listening
            
            if port_listening == expected_listening:
                result['success'] = True
                if expected_listening:
                    result['message'] = f"Port {port}/{protocol} is listening as expected"
                else:
                    result['message'] = f"Port {port}/{protocol} is not listening as expected"
            else:
                if expected_listening:
                    result['message'] = f"Port {port}/{protocol} is not listening"
                else:
                    result['message'] = f"Port {port}/{protocol} is listening but should not be"
                return result
        else:
            # If we're not checking listening status, just report it
            result['success'] = True
            result['message'] = f"Port {port}/{protocol} listening status is {port_listening}"
        
        # Check process using the port
        if 'process' in params and port_listening:
            expected_process = params['process']
            result['details']['expected_process'] = expected_process
            
            # Use lsof to check which process has the port open
            try:
                # Check if lsof is available
                if subprocess.run(['which', 'lsof'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
                    cmd = ['lsof', f'-i{protocol}:{port}', '-sTCP:LISTEN']
                    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    process_output = proc.stdout
                    
                    # Check if expected process is using the port
                    if expected_process in process_output:
                        result['details']['process_match'] = True
                    else:
                        result['success'] = False
                        result['message'] = f"Port {port}/{protocol} is not being used by '{expected_process}'"
                        result['details']['process_match'] = False
                        result['details']['actual_process'] = process_output.strip()
                else:
                    # lsof not available, skip this check
                    logger.warning("lsof not available, skipping process check")
                    result['details']['process_check_skipped'] = True
            except Exception as e:
                logger.warning(f"Error checking process for port {port}: {str(e)}")
                result['details']['process_check_error'] = str(e)
        
    except Exception as e:
        result['message'] = f"Error checking port {port}: {str(e)}"
        result['details']['error'] = str(e)
    
    return result 