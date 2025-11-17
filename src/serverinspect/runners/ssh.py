"""
SSH test runner for ServerInspect.
"""

import logging
import os
import shlex

import paramiko

from serverinspect.runners.base import BaseRunner

logger = logging.getLogger("serverinspect")


class SSHRunner(BaseRunner):
    """
    Runner that executes tests on a remote system via SSH.
    """

    def __init__(
        self,
        host,
        username=None,
        key_file=None,
        password=None,
        port=22,
        auto_add_host_key=True,
        known_hosts_file=None,
    ):
        """
        Initialize the SSH runner.

        Args:
            host (str): Remote host to connect to
            username (str): SSH username
            key_file (str): Path to SSH key file
            password (str): SSH password
            port (int): SSH port
            auto_add_host_key (bool): Whether to automatically add unknown host keys
            known_hosts_file (str): Path to known_hosts file (default: ~/.ssh/known_hosts)
        """
        self.host = host
        self.username = username
        self.key_file = key_file
        self.password = password
        self.port = port
        self.auto_add_host_key = auto_add_host_key
        self.known_hosts_file = known_hosts_file or os.path.expanduser(
            "~/.ssh/known_hosts"
        )
        self.client = None

        logger.debug(f"Initializing SSH runner for {host}")

        # Connect immediately
        self.connect()

    def connect(self):
        """
        Connect to the remote host.

        Raises:
            Exception: If connection fails
        """
        try:
            self.client = paramiko.SSHClient()

            # Use either AutoAddPolicy or load system host keys based on configuration
            if self.auto_add_host_key:
                # This is less secure but necessary for scanning unknown hosts
                logger.debug("Using AutoAddPolicy for SSH host key verification")
                self.client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy()
                )  # nosec B507
            else:
                # More secure: load system host keys and reject unknown hosts
                logger.debug(f"Using system host keys from {self.known_hosts_file}")
                self.client.load_system_host_keys(self.known_hosts_file)
                self.client.set_missing_host_key_policy(paramiko.RejectPolicy())

            connect_kwargs = {"hostname": self.host, "port": self.port, "timeout": 10}

            if self.username:
                connect_kwargs["username"] = self.username

            if self.key_file:
                connect_kwargs["key_filename"] = self.key_file

            if self.password:
                connect_kwargs["password"] = self.password

            self.client.connect(**connect_kwargs)
            logger.debug(f"Successfully connected to {self.host}")

        except Exception as e:
            logger.error(f"Failed to connect to {self.host}: {str(e)}")
            raise

    def run_command(self, command):
        """
        Run a command on the remote system.

        Args:
            command (str): Command to run

        Returns:
            str: Command output

        Raises:
            Exception: If the command fails
        """
        if not self.client:
            self.connect()

        logger.debug(f"Running command over SSH: {command}")

        # Validate command type
        if not isinstance(command, str):
            raise TypeError("Command must be a string")

        # Sanitize the command to prevent shell injection
        # This is a security measure to prevent command injection attacks
        command = shlex.quote(command)

        _stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            error = stderr.read().decode("utf-8")
            logger.debug(f"Command failed with exit status {exit_status}")
            logger.debug(f"stderr: {error}")

        return stdout.read().decode("utf-8")

    def run_command_with_status(self, command):
        """
        Run a command and return both output and exit status.

        Args:
            command (str): Command to run

        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        if not self.client:
            self.connect()

        logger.debug(f"Running command with status over SSH: {command}")

        # Validate command type
        if not isinstance(command, str):
            raise TypeError("Command must be a string")

        # Sanitize the command to prevent shell injection
        command = shlex.quote(command)

        _stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()

        return (
            exit_status,
            stdout.read().decode("utf-8"),
            stderr.read().decode("utf-8"),
        )

    def file_exists(self, path):
        """
        Check if a file exists on the remote system.

        Args:
            path (str): Path to check

        Returns:
            bool: True if the file exists
        """
        exit_code, _, _ = self.run_command_with_status(f"test -e {path}")
        return exit_code == 0

    def __del__(self):
        """Clean up resources when the object is garbage collected."""
        try:
            if hasattr(self, "client") and self.client:
                self.client.close()
                logger.debug(f"Closed SSH connection to {self.host}")
        except BaseException as e:
            logger.error(f"Error closing SSH connection: {str(e)}")
