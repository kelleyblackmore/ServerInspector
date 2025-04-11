"""
Command-line interface for ServerInspect.
"""
import os
import sys
import logging
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler

from serverinspect.core import ServerInspect
from serverinspect.config import load_config

# Set up rich console for better output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("serverinspect")

@click.group()
@click.version_option()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug):
    """ServerInspect - Test and audit server configurations."""
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

@cli.command()
@click.argument('config', type=click.Path(exists=True))
@click.option('--host', '-h', help='Remote host to test (uses SSH)')
@click.option('--username', '-u', help='SSH username for remote host')
@click.option('--key-file', '-k', type=click.Path(exists=True), help='SSH key file')
@click.option('--password', '-p', is_flag=True, help='Prompt for SSH password')
@click.option('--output-format', '-o', 
              type=click.Choice(['json', 'yaml', 'html', 'terminal']), 
              default='terminal',
              help='Output format')
@click.option('--output-file', '-f', type=click.Path(), 
              help='Output file (default: stdout)')
def run(config, host, username, key_file, password, output_format, output_file):
    """Run tests defined in a YAML configuration file."""
    try:
        ssh_password = None
        if password:
            ssh_password = click.prompt("SSH Password", hide_input=True)
            
        # Load the test configuration
        config_data = load_config(config)
        
        # Create the ServerInspect instance
        inspector = ServerInspect(
            config=config_data,
            host=host,
            username=username,
            key_file=key_file,
            password=ssh_password
        )
        
        # Run the tests
        results = inspector.run_tests()
        
        # Output the results
        inspector.output_results(
            results, 
            format=output_format, 
            output_file=output_file
        )
        
        # Exit with non-zero status if any test failed
        all_passed = all(test['result'] for test in results['tests'])
        if not all_passed:
            click.echo(f"Tests completed with failures: "
                     f"{sum(1 for t in results['tests'] if not t['result'])} failed, "
                     f"{sum(1 for t in results['tests'] if t['result'])} passed")
            sys.exit(1)
        else:
            click.echo(f"All {len(results['tests'])} tests passed!")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if logger.level == logging.DEBUG:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@cli.command()
@click.option('--output-format', '-o', 
              type=click.Choice(['json', 'yaml', 'terminal']), 
              default='terminal',
              help='Output format')
@click.option('--output-file', '-f', type=click.Path(), 
              help='Output file (default: stdout)')
def system_info(output_format, output_file):
    """Collect and display system information."""
    try:
        inspector = ServerInspect()
        info = inspector.collect_system_info()
        
        inspector.output_results(
            {"system_info": info},
            format=output_format,
            output_file=output_file
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if logger.level == logging.DEBUG:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@cli.command()
def init():
    """Initialize a new ServerInspect test file."""
    try:
        example_test = """---
# ServerInspect Test Configuration

# General information
title: Basic Server Test
description: Tests basic server functionality and configuration
author: ServerInspect User

# Test definitions
tests:
  - name: Check if nginx is installed
    type: package
    package: nginx
    installed: true
    
  - name: Check if nginx service is running
    type: service
    service: nginx
    running: true
    enabled: true
    
  - name: Check if web directory exists
    type: file
    path: /var/www/html
    exists: true
    type: directory
    
  - name: Check nginx configuration syntax
    type: command
    command: nginx -t
    exit_status: 0
    stdout:
      contains: "syntax is ok"
"""
        
        output_file = "serverinspect-test.yaml"
        
        # Check if file exists and confirm overwrite
        if os.path.exists(output_file):
            if not click.confirm(f"File {output_file} already exists. Overwrite?"):
                click.echo("Aborted.")
                return
                
        with open(output_file, "w") as f:
            f.write(example_test)
            
        click.echo(f"Created example test file: {output_file}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if logger.level == logging.DEBUG:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    cli()
