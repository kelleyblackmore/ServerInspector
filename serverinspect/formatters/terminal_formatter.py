"""
Terminal formatter for ServerInspect.
"""
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box
from rich.pretty import Pretty

from serverinspect.formatters.base import BaseFormatter

logger = logging.getLogger("serverinspect")

class TerminalFormatter(BaseFormatter):
    """
    Formatter that outputs results to the terminal using rich.
    """
    
    def __init__(self):
        """Initialize the terminal formatter."""
        self.console = Console()
    
    def format(self, results):
        """
        Format and display the test results in the terminal.
        
        Args:
            results (dict): Test results
            
        Returns:
            str: Empty string (output is directly to terminal)
        """
        logger.debug("Formatting results for terminal output")
        
        # Display title
        if 'title' in results:
            self.console.print(f"[bold cyan]{results['title']}[/bold cyan]")
        
        # Display description
        if 'description' in results:
            self.console.print(f"[italic]{results['description']}[/italic]")
            
        self.console.print()
        
        # Display host and timestamp
        self.console.print(f"Host: [bold]{results.get('host', 'localhost')}[/bold]")
        self.console.print(f"Time: [bold]{results.get('timestamp', '')}[/bold]")
        
        self.console.print()
        
        # Display system information if available
        if 'system_info' in results:
            self._print_system_info(results['system_info'])
        
        # Display test results if available
        if 'tests' in results:
            self._print_test_results(results)
        
        return ""
    
    def _print_system_info(self, system_info):
        """Print system information."""
        self.console.print("[bold]System Information[/bold]")
        
        # Create a table for basic info
        table = Table(box=box.SIMPLE)
        table.add_column("Item", style="cyan")
        table.add_column("Value")
        
        # Add basic system info to the table
        for key, value in system_info.items():
            if key not in ['cpu', 'memory', 'disk_usage', 'disk_detailed', 'memory_detailed', 'error'] and not isinstance(value, dict):
                table.add_row(key, str(value))
        
        self.console.print(table)
        self.console.print()
        
        # CPU Information
        if 'cpu' in system_info:
            cpu_panel = Panel(
                self._create_cpu_info_tree(system_info['cpu']),
                title="CPU Information",
                border_style="blue"
            )
            self.console.print(cpu_panel)
            self.console.print()
        
        # Memory Information
        if 'memory' in system_info:
            memory_panel = Panel(
                self._create_memory_info_tree(system_info['memory']),
                title="Memory Information",
                border_style="green"
            )
            self.console.print(memory_panel)
            self.console.print()
        
        # Disk Usage
        if 'disk_usage' in system_info:
            self._print_disk_usage(system_info['disk_usage'])
            self.console.print()
    
    def _create_cpu_info_tree(self, cpu_info):
        """Create a tree for CPU information."""
        tree = Tree("CPU")
        
        # Add processor count if available
        if 'processor_count' in cpu_info:
            tree.add(f"Processors: [bold]{cpu_info['processor_count']}[/bold]")
        
        # Add model name if available
        if 'model_name' in cpu_info:
            tree.add(f"Model: [bold]{cpu_info['model_name']}[/bold]")
        
        # Add vendor if available
        if 'vendor_id' in cpu_info:
            tree.add(f"Vendor: [bold]{cpu_info['vendor_id']}[/bold]")
        
        return tree
    
    def _create_memory_info_tree(self, memory_info):
        """Create a tree for memory information."""
        tree = Tree("Memory")
        
        # Add memory information
        if 'MemTotal' in memory_info:
            tree.add(f"Total: [bold]{memory_info['MemTotal']}[/bold]")
        
        if 'MemFree' in memory_info:
            tree.add(f"Free: [bold]{memory_info['MemFree']}[/bold]")
        
        if 'MemUsed' in memory_info:
            tree.add(f"Used: [bold]{memory_info['MemUsed']}[/bold]")
        
        if 'MemUsedPercent' in memory_info:
            tree.add(f"Used %: [bold]{memory_info['MemUsedPercent']}[/bold]")
        
        return tree
    
    def _print_disk_usage(self, disk_usage):
        """Print disk usage information."""
        table = Table(title="Disk Usage", box=box.SIMPLE)
        table.add_column("Filesystem", style="cyan")
        table.add_column("Size")
        table.add_column("Used")
        table.add_column("Available")
        table.add_column("Use%", style="bold")
        table.add_column("Mounted On")
        
        for disk in disk_usage:
            table.add_row(
                disk['filesystem'],
                disk['size'],
                disk['used'],
                disk['available'],
                disk['use_percent'],
                disk['mounted_on']
            )
        
        self.console.print(table)
    
    def _print_test_results(self, results):
        """Print test results."""
        summary = results.get('summary', {})
        total = summary.get('total', 0)
        passed = summary.get('passed', 0)
        failed = summary.get('failed', 0)
        
        # Display summary
        self.console.print("[bold]Test Results[/bold]")
        self.console.print(f"Total Tests: {total}")
        self.console.print(f"Passed: [green]{passed}[/green]")
        self.console.print(f"Failed: [red]{failed}[/red]")
        self.console.print()
        
        # Display individual test results
        for test in results.get('tests', []):
            self._print_test_result(test)
    
    def _print_test_result(self, test):
        """Print an individual test result."""
        name = test['name']
        test_type = test['type']
        result = test['result']
        details = test.get('details', {})
        error = test.get('error')
        
        # Create a panel for the test
        result_str = "[green]PASS[/green]" if result else "[red]FAIL[/red]"
        title = f"{name} [{test_type}] - {result_str}"
        
        # Create a tree for the details
        tree = Tree("Details")
        
        # Add error if present
        if error:
            tree.add(f"[red]Error: {error}[/red]")
        
        # Add detailed information
        for key, value in details.items():
            if isinstance(value, dict):
                subtree = tree.add(key)
                for subkey, subvalue in value.items():
                    subtree.add(f"{subkey}: {subvalue}")
            else:
                tree.add(f"{key}: {value}")
        
        # Create panel with appropriate color
        panel = Panel(
            tree,
            title=title,
            border_style="green" if result else "red"
        )
        
        self.console.print(panel)
        self.console.print()
