"""
package checker module for ServerInspect.

This module provides simple functions to check package-related aspects of a system.
"""

import logging
import subprocess

logger = logging.getLogger("serverinspect")

def check(params):
    """
    Perform a package check with the given parameters.
    
    Args:
        params (dict): Check parameters
        
    Returns:
        dict: Check result with success/failure and details
    """
    # Import the old module's functionality but with a simpler interface
    from serverinspect.test_types.package import _run_package_test
    
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    try:
        # Adapt the parameters to the old interface
        old_result = _run_package_test(None, params)
        
        # Convert the result format
        result['success'] = old_result.get('result', False)
        result['details'] = old_result.get('details', {})
        
        if result['success']:
            result['message'] = "package check passed"
        else:
            result['message'] = old_result.get('details', {}).get('error', "package check failed")
            
    except Exception as e:
        result['message'] = f"Error during package check: {str(e)}"
        logger.error(result['message'])
    
    return result
