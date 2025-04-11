"""
File test type for ServerInspect.
"""
import logging
import re
from serverinspect.test_types.base import run_test

logger = logging.getLogger("serverinspect")

def run(runner, test_config):
    """
    Run a file test.
    
    Args:
        runner: A runner instance
        test_config (dict): Test configuration
        
    Returns:
        dict: Test result
    """
    return run_test(runner, test_config, _run_file_test)

def _run_file_test(runner, test_config):
    """
    Execute a file test.
    
    Supported test options:
    - path: Path to the file
    - exists: Whether the file should exist
    - type: Type of file (file, directory, symlink)
    - content: Text that should be in the file
    - content_pattern: Regex pattern to match in the file
    - permissions: File permissions (octal, e.g. "644")
    - owner: File owner
    - group: File group
    
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
    if 'path' not in test_config:
        raise ValueError("File test requires 'path' parameter")
    
    path = test_config['path']
    result['details']['path'] = path
    
    # Check if the file exists
    exists = runner.file_exists(path)
    result['details']['exists'] = exists
    
    # If we're checking that a file should NOT exist
    if 'exists' in test_config and not test_config['exists']:
        result['result'] = not exists
        result['details']['expected'] = 'File should not exist'
        result['details']['actual'] = 'File exists' if exists else 'File does not exist'
        return result
    
    # For other checks, the file must exist
    if not exists:
        result['result'] = False
        result['details']['expected'] = 'File should exist'
        result['details']['actual'] = 'File does not exist'
        return result
    
    # Check file type
    if 'type' in test_config:
        expected_type = test_config['type']
        result['details']['expected_type'] = expected_type
        
        # Get the file type
        if expected_type == 'directory':
            exit_code, _, _ = runner.run_command_with_status(f"test -d {path}")
            is_dir = exit_code == 0
            result['details']['is_directory'] = is_dir
            if not is_dir:
                result['result'] = False
                result['details']['actual_type'] = 'not a directory'
        
        elif expected_type == 'file':
            exit_code, _, _ = runner.run_command_with_status(f"test -f {path}")
            is_file = exit_code == 0
            result['details']['is_file'] = is_file
            if not is_file:
                result['result'] = False
                result['details']['actual_type'] = 'not a regular file'
        
        elif expected_type == 'symlink':
            exit_code, _, _ = runner.run_command_with_status(f"test -L {path}")
            is_symlink = exit_code == 0
            result['details']['is_symlink'] = is_symlink
            if not is_symlink:
                result['result'] = False
                result['details']['actual_type'] = 'not a symlink'
    
    # Check file content
    if 'content' in test_config and result['result']:
        expected_content = test_config['content']
        actual_content = runner.run_command(f"cat {path}")
        
        if expected_content in actual_content:
            result['details']['content_match'] = True
        else:
            result['result'] = False
            result['details']['content_match'] = False
            result['details']['expected_content'] = expected_content
    
    # Check file content pattern
    if 'content_pattern' in test_config and result['result']:
        pattern = test_config['content_pattern']
        actual_content = runner.run_command(f"cat {path}")
        
        if re.search(pattern, actual_content):
            result['details']['pattern_match'] = True
        else:
            result['result'] = False
            result['details']['pattern_match'] = False
            result['details']['pattern'] = pattern
    
    # Check file permissions
    if 'permissions' in test_config and result['result']:
        expected_perms = test_config['permissions']
        result['details']['expected_permissions'] = expected_perms
        
        # Get the actual permissions
        actual_perms = runner.run_command(f"stat -c %a {path}").strip()
        result['details']['actual_permissions'] = actual_perms
        
        if actual_perms != expected_perms:
            result['result'] = False
    
    # Check file owner
    if 'owner' in test_config and result['result']:
        expected_owner = test_config['owner']
        result['details']['expected_owner'] = expected_owner
        
        # Get the actual owner
        actual_owner = runner.run_command(f"stat -c %U {path}").strip()
        result['details']['actual_owner'] = actual_owner
        
        if actual_owner != expected_owner:
            result['result'] = False
    
    # Check file group
    if 'group' in test_config and result['result']:
        expected_group = test_config['group']
        result['details']['expected_group'] = expected_group
        
        # Get the actual group
        actual_group = runner.run_command(f"stat -c %G {path}").strip()
        result['details']['actual_group'] = actual_group
        
        if actual_group != expected_group:
            result['result'] = False
    
    return result
