"""
File checker module for ServerInspect.

This module provides simple functions to check file-related aspects of a system.
"""

import os
import logging

logger = logging.getLogger("serverinspect")

def check(params):
    """
    Perform a file check with the given parameters.
    
    Args:
        params (dict): Check parameters, including:
            - path: Path to the file to check
            - exists: Whether the file should exist
            - contains: Text that should be contained in the file
            
    Returns:
        dict: Check result with success/failure and details
    """
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    # Required parameters
    if 'path' not in params:
        result['message'] = "Missing required parameter: path"
        return result
    
    path = params['path']
    result['details']['path'] = path
    
    # Check if the file exists
    file_exists = os.path.exists(path)
    result['details']['exists'] = file_exists
    
    # Check the existence requirement
    if 'exists' in params:
        expected_exists = params['exists']
        result['details']['expected_exists'] = expected_exists
        
        if file_exists != expected_exists:
            if expected_exists:
                result['message'] = f"File '{path}' does not exist"
            else:
                result['message'] = f"File '{path}' exists but should not"
            return result
    
    # If we're expecting the file to not exist and it doesn't, we're done
    if 'exists' in params and not params['exists'] and not file_exists:
        result['success'] = True
        result['message'] = f"File '{path}' does not exist as expected"
        return result
    
    # Only do the following checks if the file exists
    if file_exists:
        # Get file type
        file_type = "file" if os.path.isfile(path) else "directory" if os.path.isdir(path) else "other"
        result['details']['type'] = file_type
        
        # Check content if required
        if 'contains' in params and file_type == 'file':
            expected_content = params['contains']
            try:
                with open(path, 'r') as f:
                    content = f.read()
                has_content = expected_content in content
                result['details']['has_content'] = has_content
                if not has_content:
                    result['message'] = f"File '{path}' does not contain '{expected_content}'"
                    return result
            except Exception as e:
                result['message'] = f"Error reading file '{path}': {str(e)}"
                return result
        
        # All checks passed
        result['success'] = True
        result['message'] = f"File '{path}' passed all checks"
    
    return result
