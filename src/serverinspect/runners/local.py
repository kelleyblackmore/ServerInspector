"""
Local test runner for ServerInspect.
"""
import os
import subprocess
import logging
import shutil
from pathlib import Path

logger = logging.getLogger("serverinspect")

class LocalRunner:
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
        result = subprocess.run(
            command, 
            shell=True, 
            check=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
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
        result = subprocess.run(
            command, 
            shell=True, 
            check=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
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
    
    def service_status(self, service_name):
        """
        Check the status of a service.
        
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
        if shutil.which('systemctl'):
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
        if shutil.which('service'):
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
                    if os.path.exists("/etc/init.d"):
                        rc_dirs = Path("/etc/rc.d") if os.path.exists("/etc/rc.d") else Path("/etc")
                        for i in range(2, 6):  # Check runlevels 2-5
                            rc_dir = rc_dirs / f"rc{i}.d"
                            if rc_dir.exists():
                                for file in rc_dir.glob(f"S*{service_name}"):
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
        Check if a package is installed.
        
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
            pm_path = shutil.which(pm_name)
            if pm_path:
                try:
                    exit_code, stdout, _ = self.run_command_with_status(
                        f"{pm_path} {pm_arg} {package_name}"
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
        Check if a process is running.
        
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
            if shutil.which('pgrep'):
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
