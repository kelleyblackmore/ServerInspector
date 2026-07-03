"""
Local test runner for serverinspector.
"""

import logging
import os
import shlex
import subprocess

from serverinspector.runners.base import BaseRunner

logger = logging.getLogger("serverinspector")


def _prepare_command(command):
    """
    Prepare a command string for subprocess.run with shell=False.

    On POSIX, split into an argument list. On Windows, pass the string
    through: shlex.split would mangle backslashes in paths, and
    CreateProcess parses the command line natively.
    """
    if os.name == "nt":
        return command
    return shlex.split(command)


class LocalRunner(BaseRunner):
    """
    Runner that executes tests on the local system.
    """

    def __init__(self):
        """Initialize the local runner."""
        logger.debug("Initializing local runner")

    def run_command(self, command):
        """
        Run a command on the local system.

        Args:
            command (str): Command to run

        Returns:
            str: Command output

        Raises:
            subprocess.CalledProcessError: If the command fails
        """
        logger.debug(f"Running command: {command}")
        command_args = _prepare_command(command)
        result = subprocess.run(
            command_args,
            shell=False,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if result.returncode != 0:
            logger.debug(f"Command failed with exit code {result.returncode}")
            logger.debug(f"stderr: {result.stderr}")

        return result.stdout

    def run_command_with_status(self, command):
        """
        Run a command and return both output and exit status.

        Args:
            command (str): Command to run

        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        logger.debug(f"Running command with status: {command}")
        command_args = _prepare_command(command)
        result = subprocess.run(
            command_args,
            shell=False,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return (result.returncode, result.stdout, result.stderr)

    def file_exists(self, path):
        """
        Check if a file exists.

        Args:
            path (str): Path to check

        Returns:
            bool: True if the file exists
        """
        return os.path.exists(path)
