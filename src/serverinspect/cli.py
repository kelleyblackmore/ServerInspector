"""
Command-line interface for ServerInspect.
"""

import logging
import os
import sys

import click
from rich.console import Console
from rich.logging import RichHandler

from serverinspect.config import load_config
from serverinspect.core import ServerInspect

# Import modules that might not be available (they'll be handled properly inside the functions)
try:
    pass
except ImportError:
    pass  # This will be handled in the check function

# Set up rich console for better output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)],
)
logger = logging.getLogger("serverinspect")


@click.group()
@click.version_option()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug):
    """ServerInspect - Test and audit server configurations."""
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")


@cli.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--host", "-h", help="Remote host to test (uses SSH)")
@click.option("--username", "-u", help="SSH username for remote host")
@click.option("--key-file", "-k", type=click.Path(exists=True), help="SSH key file")
@click.option("--password", "-p", is_flag=True, help="Prompt for SSH password")
@click.option(
    "--output-format",
    "-o",
    type=click.Choice(["json", "yaml", "html", "terminal"]),
    default="terminal",
    help="Output format",
)
@click.option(
    "--output-file", "-f", type=click.Path(), help="Output file (default: stdout)"
)
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
            password=ssh_password,
        )

        # Run the tests
        results = inspector.run_tests()

        # Output the results
        inspector.output_results(results, format=output_format, output_file=output_file)

        # Exit with non-zero status if any test failed
        all_passed = all(test["result"] for test in results["tests"])
        if not all_passed:
            click.echo(
                f"Tests completed with failures: "
                f"{sum(1 for t in results['tests'] if not t['result'])} failed, "
                f"{sum(1 for t in results['tests'] if t['result'])} passed"
            )
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
@click.option(
    "--output-format",
    "-o",
    type=click.Choice(["json", "yaml", "terminal"]),
    default="terminal",
    help="Output format",
)
@click.option(
    "--output-file", "-f", type=click.Path(), help="Output file (default: stdout)"
)
def system_info(output_format, output_file):
    """Collect and display system information."""
    try:
        inspector = ServerInspect()
        info = inspector.collect_system_info()

        inspector.output_results(
            {"system_info": info}, format=output_format, output_file=output_file
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


if __name__ == "__main__":
    cli()


@cli.command()
@click.argument("check_type")
@click.argument("target")
@click.option(
    "--exists/--not-exists",
    default=None,
    help="For file/package checks: whether the file/package should exist",
)
@click.option(
    "--contains",
    help="For file/command checks: text that should be contained in the output",
)
@click.option("--exit-code", type=int, help="For command checks: expected exit code")
@click.option(
    "--running/--not-running",
    default=None,
    help="For service/process checks: whether it should be running",
)
@click.option(
    "--listening/--not-listening",
    default=None,
    help="For port checks: whether the port should be listening",
)
@click.option(
    "--protocol",
    type=click.Choice(["tcp", "udp"]),
    default="tcp",
    help="For port checks: protocol to check",
)
def check(check_type, target, **options):
    """
    Perform a simple check against the target.

    CHECK_TYPE can be: file, command, service, process, package, port
    TARGET is what to check (a path, command, service, etc.)
    """
    try:
        # Verify that the checkers module is available
        try:
            from serverinspect.checkers import get_checker
        except ImportError:
            logger.error("The 'serverinspect.checkers' module is not available.")
            console.print(
                "[bold red]Error:[/bold red] The checkers module is not installed or not in the Python path."
            )
            console.print(
                "Make sure you've installed ServerInspect correctly and the src directory is in your Python path."
            )
            sys.exit(1)

        # Prepare parameters based on the check type
        params = {"name": f"Check {target}"}

        if check_type == "file":
            params["path"] = target
            if options.get("exists") is not None:
                params["exists"] = options["exists"]
            if options.get("contains"):
                params["contains"] = options["contains"]

        elif check_type == "command":
            params["command"] = target
            if options.get("exit_code") is not None:
                params["exit_code"] = options["exit_code"]
            if options.get("contains"):
                params["stdout_contains"] = options["contains"]

        elif check_type in ("service", "process"):
            if check_type == "service":
                params["service"] = target
            else:
                params["process_name"] = target

            if options.get("running") is not None:
                params["running"] = options["running"]

        elif check_type == "package":
            params["package"] = target
            if options.get("exists") is not None:
                params["installed"] = options["exists"]

        elif check_type == "port":
            params["port"] = target
            if options.get("listening") is not None:
                params["listening"] = options["listening"]
            if options.get("protocol"):
                params["protocol"] = options["protocol"]

        # Get the appropriate checker and run it
        try:
            checker = get_checker(check_type)
            result = checker.check(params)

            # Display the result
            if result["success"]:
                click.secho(f"✓ {result['message']}", fg="green")
            else:
                click.secho(f"✗ {result['message']}", fg="red")

            # Show details if any
            if result["details"]:
                click.echo("Details:")
                for key, value in result["details"].items():
                    click.echo(f"  {key}: {value}")
        except ValueError as e:
            # Invalid checker type or other validation error
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)
        except ImportError as e:
            # Module not found - likely a path issue
            logger.error(f"Failed to import module: {str(e)}")
            console.print(
                f"[bold red]Error:[/bold red] Could not import the needed module: {str(e)}"
            )
            console.print(
                "This might be due to incomplete installation or Python path issues."
            )
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if logger.level == logging.DEBUG:
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)
