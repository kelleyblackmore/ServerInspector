"""
Test runners for serverinspector.
"""

import logging

logger = logging.getLogger("serverinspector")


def get_runner(host=None, port=22, username=None, key_file=None, password=None):
    """
    Get the appropriate runner based on the connection parameters.

    Args:
        host (str): Remote host to connect to (None for local)
        port (int): SSH port (default: 22)
        username (str): SSH username for remote host
        key_file (str): Path to SSH key file
        password (str): SSH password

    Returns:
        Runner: An instance of a Runner class
    """
    if host:
        # Use SSH runner for remote hosts
        from serverinspector.runners.ssh import SSHRunner

        return SSHRunner(host, username, key_file, password, port)
    else:
        # Use local runner for local tests
        from serverinspector.runners.local import LocalRunner

        return LocalRunner()
