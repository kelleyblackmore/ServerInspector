"""
Test runners for ServerInspect.
"""
import logging

logger = logging.getLogger("serverinspect")

def get_runner(host=None, username=None, key_file=None, password=None):
    """
    Get the appropriate runner based on the connection parameters.
    
    Args:
        host (str): Remote host to connect to (None for local)
        username (str): SSH username for remote host
        key_file (str): Path to SSH key file
        password (str): SSH password
        
    Returns:
        Runner: An instance of a Runner class
    """
    if host:
        # Use SSH runner for remote hosts
        from serverinspect.runners.ssh import SSHRunner
        return SSHRunner(host, username, key_file, password)
    else:
        # Use local runner for local tests
        from serverinspect.runners.local import LocalRunner
        return LocalRunner()
