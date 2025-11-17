#!/usr/bin/env python3
"""
Test script to demonstrate enhanced package manager and service features.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from serverinspect.runners.local import LocalRunner
from serverinspect.package_managers import get_registry
from serverinspect.service_managers import get_service_status
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()


def test_package_managers():
    """Test the package manager registry."""
    console.print("\n[bold cyan]═══ Package Manager Registry Test ═══[/bold cyan]\n")

    runner = LocalRunner()
    registry = get_registry()

    # Detect available package managers
    available = registry.detect_available(runner)

    if not available:
        console.print("[red]No package managers detected![/red]")
        return

    # Create table of detected package managers
    table = Table(title="Detected Package Managers")
    table.add_column("Name", style="cyan")
    table.add_column("Binary", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("Description", style="white")

    for pm in available:
        table.add_row(pm.name, pm.binary, str(pm.priority), pm.description)

    console.print(table)

    # Test checking a package
    console.print("\n[bold]Testing package checks:[/bold]")
    
    test_packages = ["bash", "python3", "curl", "git", "vim"]
    
    for package in test_packages:
        result = registry.check_package(runner, package)
        if result["installed"]:
            console.print(
                f"  ✓ [green]{package}[/green]: "
                f"version {result['version']} "
                f"(via {result['package_manager']})"
            )
        else:
            console.print(f"  ✗ [red]{package}[/red]: not installed")


def test_service_status():
    """Test enhanced service status."""
    console.print("\n[bold cyan]═══ Enhanced Service Status Test ═══[/bold cyan]\n")

    runner = LocalRunner()
    
    # Test services to check
    test_services = ["sshd", "cron", "systemd-journald", "docker"]

    for service_name in test_services:
        console.print(f"\n[bold]Service: {service_name}[/bold]")
        
        status = get_service_status(runner, service_name)
        status_dict = status.to_dict()

        # Create a tree view of service details
        tree = Tree(f"[cyan]{service_name}[/cyan]")
        
        # Basic info
        basic = tree.add("[yellow]Basic Info[/yellow]")
        basic.add(f"Exists: {'✓' if status_dict['exists'] else '✗'} {status_dict['exists']}")
        basic.add(f"Running: {'✓' if status_dict['running'] else '✗'} {status_dict['running']}")
        basic.add(f"Enabled: {'✓' if status_dict['enabled'] else '✗'} {status_dict['enabled']}")
        basic.add(f"Manager: {status_dict['service_manager']}")

        # Enhanced info (if available)
        if status_dict.get('state'):
            enhanced = tree.add("[yellow]Enhanced Details[/yellow]")
            if status_dict.get('state'):
                enhanced.add(f"State: {status_dict['state']}")
            if status_dict.get('substate'):
                enhanced.add(f"Substate: {status_dict['substate']}")
            if status_dict.get('pid'):
                enhanced.add(f"PID: {status_dict['pid']}")
            if status_dict.get('memory_usage'):
                enhanced.add(f"Memory: {status_dict['memory_usage']}")
            if status_dict.get('restart_count') is not None:
                enhanced.add(f"Restarts: {status_dict['restart_count']}")
            if status_dict.get('masked'):
                enhanced.add(f"Masked: {status_dict['masked']}")
            if status_dict.get('uptime'):
                enhanced.add(f"Uptime: {status_dict['uptime']}")

        # Dependencies (if any)
        if status_dict.get('dependencies'):
            deps = tree.add(f"[yellow]Dependencies ({len(status_dict['dependencies'])})[/yellow]")
            for dep in status_dict['dependencies'][:5]:  # Show first 5
                deps.add(dep)
            if len(status_dict['dependencies']) > 5:
                deps.add(f"... and {len(status_dict['dependencies']) - 5} more")

        # Error (if any)
        if status_dict.get('error'):
            tree.add(f"[red]Error: {status_dict['error']}[/red]")

        console.print(tree)


def test_backward_compatibility():
    """Test that old API still works."""
    console.print("\n[bold cyan]═══ Backward Compatibility Test ═══[/bold cyan]\n")

    runner = LocalRunner()

    # Test old package_status API
    console.print("[bold]Testing package_status (legacy):[/bold]")
    result = runner.package_status("bash")
    console.print(f"  bash installed: {result['installed']}")
    console.print(f"  version: {result.get('version', 'unknown')}")
    console.print(f"  package_manager: {result.get('package_manager', 'unknown')}")

    # Test old service_status API with enhanced=False
    console.print("\n[bold]Testing service_status (legacy):[/bold]")
    result = runner.service_status("sshd", enhanced=False)
    console.print(f"  sshd exists: {result['exists']}")
    console.print(f"  sshd running: {result['running']}")
    console.print(f"  sshd enabled: {result['enabled']}")


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold green]ServerInspect Enhanced Features Demo[/bold green]\n"
        "Testing package manager registry and enhanced service status",
        border_style="green"
    ))

    try:
        test_package_managers()
        test_service_status()
        test_backward_compatibility()

        console.print("\n[bold green]✓ All tests completed![/bold green]\n")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
