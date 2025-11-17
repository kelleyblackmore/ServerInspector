#!/usr/bin/env python3
"""
Multi-OS Integration Test Runner for ServerInspector

This script orchestrates testing ServerInspector against multiple Linux
distributions running in Docker containers via SSH.
"""

import os
import sys
import json
import yaml
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.tree import Tree

console = Console()

# Test configuration
DISTRIBUTIONS = {
    "ubuntu": {
        "name": "Ubuntu 24.04",
        "ssh_port": 2201,
        "container": "serverinspect-ubuntu",
        "configs": ["common-tests.yaml", "ubuntu-tests.yaml"],
        "package_manager": "apt/dpkg",
        "service_manager": "systemd"
    },
    "debian": {
        "name": "Debian 12",
        "ssh_port": 2202,
        "container": "serverinspect-debian",
        "configs": ["common-tests.yaml", "debian-tests.yaml"],
        "package_manager": "apt/dpkg",
        "service_manager": "systemd"
    },
    "fedora": {
        "name": "Fedora 40",
        "ssh_port": 2203,
        "container": "serverinspect-fedora",
        "configs": ["common-tests.yaml", "fedora-tests.yaml"],
        "package_manager": "dnf/rpm",
        "service_manager": "systemd"
    },
    "centos": {
        "name": "CentOS Stream 9",
        "ssh_port": 2204,
        "container": "serverinspect-centos",
        "configs": ["common-tests.yaml", "centos-tests.yaml"],
        "package_manager": "dnf/yum/rpm",
        "service_manager": "systemd"
    },
    "alpine": {
        "name": "Alpine 3.19",
        "ssh_port": 2205,
        "container": "serverinspect-alpine",
        "configs": ["common-tests.yaml", "alpine-tests.yaml"],
        "package_manager": "apk",
        "service_manager": "OpenRC"
    },
    "arch": {
        "name": "Arch Linux",
        "ssh_port": 2206,
        "container": "serverinspect-arch",
        "configs": ["common-tests.yaml", "arch-tests.yaml"],
        "package_manager": "pacman",
        "service_manager": "systemd"
    },
    "opensuse": {
        "name": "openSUSE Tumbleweed",
        "ssh_port": 2207,
        "container": "serverinspect-opensuse",
        "configs": ["common-tests.yaml", "opensuse-tests.yaml"],
        "package_manager": "zypper/rpm",
        "service_manager": "systemd"
    }
}

SSH_CONFIG = {
    "username": "testuser",
    "password": "testpass",
    "hostname": "localhost"
}


class TestRunner:
    """Orchestrates running ServerInspector tests against multiple distributions."""
    
    def __init__(self, script_dir: Path):
        self.script_dir = script_dir
        self.config_dir = script_dir / "configs"
        self.results_dir = script_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.results: Dict[str, Any] = {}
        self.start_time = datetime.now()
    
    def check_docker_environment(self) -> bool:
        """Verify Docker containers are running."""
        console.print("\n[bold blue]Checking Docker Environment[/bold blue]")
        
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                cwd=self.script_dir,
                capture_output=True,
                text=True
            )
            
            # Check if command failed (ignore warnings on stderr)
            if result.returncode != 0 and not result.stdout.strip():
                console.print(f"[red]❌ Docker command failed: {result.stderr}[/red]")
                return False
            
            if not result.stdout.strip():
                console.print("[red]❌ No containers running[/red]")
                console.print("[yellow]Run: docker compose up -d[/yellow]")
                return False
            
            # Parse container data - handle both single object and array formats
            container_data = json.loads(result.stdout)
            if isinstance(container_data, dict):
                containers = [container_data]
            else:
                containers = container_data
            
            running_count = sum(1 for c in containers if c.get("State") == "running")
            console.print(f"[green]✓ {running_count}/{len(DISTRIBUTIONS)} containers running[/green]")
            
            for dist_key, dist_info in DISTRIBUTIONS.items():
                container_name = dist_info["container"]
                is_running = any(
                    c.get("Name") == container_name and c.get("State") == "running"
                    for c in containers
                )
                
                status = "[green]✓[/green]" if is_running else "[red]✗[/red]"
                console.print(f"  {status} {dist_info['name']}: {container_name}")
            
            return running_count > 0
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error checking Docker: {e}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            return False
    
    def wait_for_ssh(self, port: int, timeout: int = 30) -> bool:
        """Wait for SSH to be available on a port."""
        import socket
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                
                if result == 0:
                    return True
            except Exception:
                pass
            
            time.sleep(1)
        
        return False
    
    def run_serverinspector_test(
        self,
        dist_key: str,
        config_file: str
    ) -> Optional[Dict[str, Any]]:
        """Run ServerInspector against a specific distribution."""
        dist_info = DISTRIBUTIONS[dist_key]
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            console.print(f"[red]Config not found: {config_path}[/red]")
            return None
        
        # Build serverinspect command using the new CLI format
        cmd = [
            "serverinspect",
            "run",
            str(config_path),
            "--host", SSH_CONFIG["hostname"],
            "--port", str(dist_info["ssh_port"]),
            "--username", SSH_CONFIG["username"],
            "--password-stdin", SSH_CONFIG["password"],
            "--output-format", "json"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout per test
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    console.print(f"[yellow]Warning: Invalid JSON output[/yellow]")
                    return {
                        "error": "Invalid JSON output",
                        "stdout": result.stdout[:500],
                        "stderr": result.stderr[:500]
                    }
            else:
                return {
                    "error": f"Command failed with exit code {result.returncode}",
                    "stdout": result.stdout[:500] if result.stdout else "",
                    "stderr": result.stderr[:500] if result.stderr else ""
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Test timeout (>120s)"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_tests_for_distribution(self, dist_key: str) -> Dict[str, Any]:
        """Run all tests for a specific distribution."""
        dist_info = DISTRIBUTIONS[dist_key]
        
        console.print(f"\n[bold cyan]Testing {dist_info['name']}[/bold cyan]")
        console.print(f"  Port: {dist_info['ssh_port']}")
        console.print(f"  Package Manager: {dist_info['package_manager']}")
        console.print(f"  Service Manager: {dist_info['service_manager']}")
        
        # Wait for SSH
        console.print(f"  Waiting for SSH on port {dist_info['ssh_port']}...", end=" ")
        if not self.wait_for_ssh(dist_info['ssh_port']):
            console.print("[red]✗ SSH not available[/red]")
            return {
                "distribution": dist_info['name'],
                "status": "failed",
                "error": "SSH not available",
                "tests": []
            }
        console.print("[green]✓[/green]")
        
        # Run each config file
        all_tests = []
        total_passed = 0
        total_failed = 0
        
        for config_file in dist_info['configs']:
            console.print(f"  Running: {config_file}...", end=" ")
            
            result = self.run_serverinspector_test(dist_key, config_file)
            
            if result and "error" not in result:
                # Parse test results
                test_groups = result.get("test_groups", [])
                for group in test_groups:
                    tests = group.get("tests", [])
                    for test in tests:
                        all_tests.append(test)
                        if test.get("status") == "passed":
                            total_passed += 1
                        else:
                            total_failed += 1
                
                console.print(f"[green]✓ {len(test_groups)} groups[/green]")
            else:
                error_msg = result.get("error", "Unknown error") if result else "No result"
                console.print(f"[red]✗ {error_msg}[/red]")
                all_tests.append({
                    "name": config_file,
                    "status": "error",
                    "error": error_msg
                })
                total_failed += 1
        
        summary = {
            "distribution": dist_info['name'],
            "container": dist_info['container'],
            "package_manager": dist_info['package_manager'],
            "service_manager": dist_info['service_manager'],
            "total_tests": total_passed + total_failed,
            "passed": total_passed,
            "failed": total_failed,
            "pass_rate": round(total_passed / (total_passed + total_failed) * 100, 1) if (total_passed + total_failed) > 0 else 0,
            "tests": all_tests
        }
        
        console.print(f"  [bold]Results: {total_passed} passed, {total_failed} failed[/bold]")
        
        return summary
    
    def run_all_tests(self, distributions: Optional[List[str]] = None):
        """Run tests against all (or specified) distributions."""
        if distributions is None:
            distributions = list(DISTRIBUTIONS.keys())
        
        console.print(Panel.fit(
            "[bold]ServerInspector Multi-OS Integration Test Suite[/bold]\n"
            f"Testing {len(distributions)} distributions",
            border_style="blue"
        ))
        
        # Check Docker environment
        if not self.check_docker_environment():
            console.print("\n[red]Docker environment check failed. Exiting.[/red]")
            return
        
        # Run tests for each distribution
        for dist_key in distributions:
            if dist_key not in DISTRIBUTIONS:
                console.print(f"[yellow]Skipping unknown distribution: {dist_key}[/yellow]")
                continue
            
            self.results[dist_key] = self.run_tests_for_distribution(dist_key)
        
        # Generate summary
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print a summary table of all test results."""
        console.print("\n[bold blue]Test Results Summary[/bold blue]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Distribution", style="cyan", width=20)
        table.add_column("Package Mgr", style="yellow", width=15)
        table.add_column("Service Mgr", style="yellow", width=12)
        table.add_column("Total", justify="right", width=8)
        table.add_column("Passed", justify="right", width=8)
        table.add_column("Failed", justify="right", width=8)
        table.add_column("Pass Rate", justify="right", width=10)
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for dist_key, result in self.results.items():
            total_tests += result.get("total_tests", 0)
            total_passed += result.get("passed", 0)
            total_failed += result.get("failed", 0)
            
            pass_rate = result.get("pass_rate", 0)
            pass_rate_str = f"{pass_rate}%"
            
            # Color code pass rate
            if pass_rate >= 90:
                pass_rate_str = f"[green]{pass_rate_str}[/green]"
            elif pass_rate >= 70:
                pass_rate_str = f"[yellow]{pass_rate_str}[/yellow]"
            else:
                pass_rate_str = f"[red]{pass_rate_str}[/red]"
            
            table.add_row(
                result.get("distribution", dist_key),
                result.get("package_manager", "?"),
                result.get("service_manager", "?"),
                str(result.get("total_tests", 0)),
                f"[green]{result.get('passed', 0)}[/green]",
                f"[red]{result.get('failed', 0)}[/red]",
                pass_rate_str
            )
        
        console.print(table)
        
        # Overall summary
        overall_pass_rate = round(total_passed / total_tests * 100, 1) if total_tests > 0 else 0
        console.print(f"\n[bold]Overall Results:[/bold]")
        console.print(f"  Total Tests: {total_tests}")
        console.print(f"  Passed: [green]{total_passed}[/green]")
        console.print(f"  Failed: [red]{total_failed}[/red]")
        console.print(f"  Pass Rate: [bold]{overall_pass_rate}%[/bold]")
        
        duration = datetime.now() - self.start_time
        console.print(f"\n[dim]Test duration: {duration}[/dim]")
    
    def save_results(self):
        """Save test results to JSON and YAML files."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        results_data = {
            "timestamp": self.start_time.isoformat(),
            "duration": str(datetime.now() - self.start_time),
            "distributions": self.results
        }
        
        # Save JSON
        json_file = self.results_dir / f"test_results_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(results_data, f, indent=2)
        console.print(f"\n[green]Results saved to: {json_file}[/green]")
        
        # Save YAML
        yaml_file = self.results_dir / f"test_results_{timestamp}.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(results_data, f, default_flow_style=False, sort_keys=False)
        console.print(f"[green]Results saved to: {yaml_file}[/green]")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run ServerInspector integration tests against multiple Linux distributions"
    )
    parser.add_argument(
        "--distributions",
        "-d",
        nargs="+",
        choices=list(DISTRIBUTIONS.keys()),
        help="Specific distributions to test (default: all)"
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available distributions and exit"
    )
    
    args = parser.parse_args()
    
    if args.list:
        console.print("\n[bold]Available Distributions:[/bold]\n")
        for key, info in DISTRIBUTIONS.items():
            console.print(f"  [cyan]{key:12}[/cyan] - {info['name']:25} "
                         f"(Port: {info['ssh_port']}, PM: {info['package_manager']}, "
                         f"SM: {info['service_manager']})")
        return
    
    script_dir = Path(__file__).parent
    runner = TestRunner(script_dir)
    runner.run_all_tests(args.distributions)


if __name__ == "__main__":
    main()
