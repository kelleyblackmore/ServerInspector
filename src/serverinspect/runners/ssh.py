"""
SSH test runner for ServerInspect.
"""
import os
import logging
import paramiko

logger = logging.getLogger("serverinspect")

class SSHRunner:
    """
    Runner that executes tests on a remote system via SSH.
    """
    
    def __init__(self, host, username=None, key_file=None, password=None, port=22):
        """
        Initialize the SSH runner.
        
        Args:
            host (str): Remote host to connect to
            username (str): SSH username
            key_file (str): Path to SSH key file
            password (str): SSH password
            port (int): SSH port
        """
        self.host = host
        self.username = username
        self.key_file = key_file
        self.password = password
        self.port = port
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
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': self.host,
                'port': self.port,
                'timeout': 10
            }
            
            if self.username:
                connect_kwargs['username'] = self.username
            
            if self.key_file:
                connect_kwargs['key_filename'] = self.key_file
            
            if self.password:
                connect_kwargs['password'] = self.password
            
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
        
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            error = stderr.read().decode('utf-8')
            logger.debug(f"Command failed with exit status {exit_status}")
            logger.debug(f"stderr: {error}")
        
        return stdout.read().decode('utf-8')
    
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
        
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        
        return (
            exit_status,
            stdout.read().decode('utf-8'),
            stderr.read().decode('utf-8')
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
    
    def service_status(self, service_name):
        """
        Check the status of a service on the remote system.
        
        Args:
            service_name (str): Name of the service
            
        Returns:
            dict: Service status information
        """
        result = {
            'exists': False,
            'running': False,
            'enabled': False,
            'error': None
        }
        
        # Try systemctl first (systemd)
        exit_code, _, _ = self.run_command_with_status("which systemctl")
        if exit_code == 0:
            try:
                # Check if service exists
                exit_code, _, _ = self.run_command_with_status(
                    f"systemctl list-unit-files | grep -q {service_name}.service"
                )
                result['exists'] = exit_code == 0
                
                if result['exists']:
                    # Check if service is running
                    exit_code, _, _ = self.run_command_with_status(
                        f"systemctl is-active --quiet {service_name}"
                    )
                    result['running'] = exit_code == 0
                    
                    # Check if service is enabled
                    exit_code, _, _ = self.run_command_with_status(
                        f"systemctl is-enabled --quiet {service_name}"
                    )
                    result['enabled'] = exit_code == 0
                    
                return result
            except Exception as e:
                result['error'] = str(e)
                logger.debug(f"Error checking service with systemctl: {str(e)}")
        
        # Try service command (SysV init)
        exit_code, _, _ = self.run_command_with_status("which service")
        if exit_code == 0:
            try:
                # Check if service exists
                exit_code, _, _ = self.run_command_with_status(
                    f"service {service_name} status"
                )
                result['exists'] = exit_code != 127  # 127 = command not found
                
                if result['exists']:
                    # Parsing the output to determine if it's running
                    _, stdout, _ = self.run_command_with_status(
                        f"service {service_name} status"
                    )
                    result['running'] = "running" in stdout.lower()
                    
                    # Check if service is enabled (might not work on all systems)
                    exit_code, _, _ = self.run_command_with_status("ls /etc/init.d")
                    if exit_code == 0:
                        for i in range(2, 6):  # Check runlevels 2-5
                            exit_code, stdout, _ = self.run_command_with_status(
                                f"ls /etc/rc{i}.d/S*{service_name} 2>/dev/null || ls /etc/rc.d/rc{i}.d/S*{service_name} 2>/dev/null"
                            )
                            if exit_code == 0 and stdout.strip():
                                result['enabled'] = True
                                break
                
                return result
            except Exception as e:
                if not result['error']:  # Don't overwrite systemctl error
                    result['error'] = str(e)
                logger.debug(f"Error checking service with service command: {str(e)}")
        
        # If we get here, we couldn't check the service
        if not result['error']:
            result['error'] = "Could not determine service status (no systemctl or service command found)"
            
        return result
    
    def package_status(self, package_name):
        """
        Check if a package is installed on the remote system.
        
        Args:
            package_name (str): Name of the package
            
        Returns:
            dict: Package status information
        """
        result = {
            'installed': False,
            'version': None,
            'error': None
        }
        
        # Try to detect the package manager
        package_managers = [
            ('dpkg', '-s'),               # Debian, Ubuntu
            ('rpm', '-q'),                # Red Hat, CentOS, Fedora
            ('pacman', '-Q'),             # Arch Linux
            ('pkg_info', '-E'),           # FreeBSD
            ('pkg', 'info'),              # FreeBSD newer
            ('brew', 'list --versions'),  # macOS Homebrew
        ]
        
        for pm_name, pm_arg in package_managers:
            exit_code, _, _ = self.run_command_with_status(f"which {pm_name}")
            if exit_code == 0:
                try:
                    exit_code, stdout, _ = self.run_command_with_status(
                        f"{pm_name} {pm_arg} {package_name}"
                    )
                    result['installed'] = exit_code == 0
                    
                    if result['installed'] and stdout:
                        # Try to extract version information
                        if pm_name == 'dpkg':
                            for line in stdout.splitlines():
                                if line.startswith('Version:'):
                                    result['version'] = line.split(':', 1)[1].strip()
                                    break
                        elif pm_name == 'rpm' or pm_name == 'pacman':
                            # Output format: package-name-version
                            parts = stdout.strip().split('-')
                            if len(parts) >= 3:
                                result['version'] = '-'.join(parts[2:])
                        elif pm_name == 'brew':
                            if package_name in stdout:
                                result['version'] = stdout.split()[1]
                        else:
                            # Generic: just use first line of output as version
                            result['version'] = stdout.splitlines()[0].strip()
                    
                    return result
                except Exception as e:
                    result['error'] = str(e)
                    logger.debug(f"Error checking package with {pm_name}: {str(e)}")
        
        # If we get here, we couldn't check the package
        if not result['error']:
            result['error'] = "Could not determine package status (no supported package manager found)"
            
        return result
    
    def process_status(self, process_name):
        """
        Check if a process is running on the remote system.
        
        Args:
            process_name (str): Name of the process
            
        Returns:
            dict: Process status information
        """
        result = {
            'running': False,
            'count': 0,
            'error': None
        }
        
        try:
            # Use pgrep if available
            exit_code, _, _ = self.run_command_with_status("which pgrep")
            if exit_code == 0:
                exit_code, stdout, _ = self.run_command_with_status(
                    f"pgrep -f {process_name} | wc -l"
                )
                if exit_code == 0:
                    result['count'] = int(stdout.strip())
                    result['running'] = result['count'] > 0
            else:
                # Fall back to ps and grep
                exit_code, stdout, _ = self.run_command_with_status(
                    f"ps aux | grep -v grep | grep {process_name} | wc -l"
                )
                if exit_code == 0:
                    result['count'] = int(stdout.strip())
                    result['running'] = result['count'] > 0
        except Exception as e:
            result['error'] = str(e)
            logger.debug(f"Error checking process: {str(e)}")
        
        return result
    
    def __del__(self):
        """Clean up the SSH connection when the object is destroyed."""
        if self.client:
            try:
                self.client.close()
                logger.debug(f"Closed SSH connection to {self.host}")
            except:
                pass
