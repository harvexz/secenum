"""Command-line interface for SecEnum."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional
import json
import logging
import sys
from datetime import datetime

from ..core.enumerator import SystemEnumerator

console = Console()
logger = logging.getLogger(__name__)

def setup_logging(debug: bool):
    """Configure logging based on verbosity level."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def format_size(size_bytes: int) -> str:
    """Format byte sizes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"

@click.group()
@click.option("--debug/--no-debug", default=False, help="Enable debug logging")
def cli(debug: bool):
    """SecEnum: Advanced System Software Enumeration & Security Assessment Tool"""
    setup_logging(debug)

@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "text"]), default="text")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output to console")
def scan(output: Optional[str], format: str, quiet: bool):
    """Perform complete system enumeration."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=quiet
        ) as progress:
            # Initialize enumerator
            progress.add_task("Initializing system enumerator...", total=None)
            enumerator = SystemEnumerator()

            # Perform enumeration
            progress.add_task("Performing system enumeration...", total=None)
            results = enumerator.enumerate_all()

            if not quiet:
                display_results(results)

            if output:
                save_results(results, output, format)
                console.print(f"\n[green]Results saved to: {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Enumeration failed")
        sys.exit(1)

@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def analyze(output: Optional[str]):
    """Perform security analysis."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Performing security analysis...", total=None)
            
            enumerator = SystemEnumerator()
            results = enumerator.analyze_security()
            
            progress.update(task, completed=True)
            
            display_security_analysis(results)
            
            if output:
                save_results(results, output, "json")
                console.print(f"\n[green]Security analysis saved to: {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Security analysis failed")
        sys.exit(1)

def display_results(results: dict):
    """Display enumeration results in a formatted table."""
    # System Information
    console.print("\n[bold blue]System Information[/bold blue]")
    sys_info = results["system_info"]
    sys_table = Table(show_header=False)
    sys_table.add_column("Property")
    sys_table.add_column("Value")
    
    for key, value in sys_info.items():
        if isinstance(value, dict):
            value = json.dumps(value, indent=2)
        sys_table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(sys_table)

    # Package Information
    console.print("\n[bold blue]Package Summary[/bold blue]")
    pkg_table = Table(show_header=True)
    pkg_table.add_column("Metric")
    pkg_table.add_column("Value")
    
    packages = results.get("packages", {})
    pkg_table.add_row("Total Packages", str(len(packages)))
    console.print(pkg_table)

    # Service Information
    console.print("\n[bold blue]Service Summary[/bold blue]")
    svc_table = Table(show_header=True)
    svc_table.add_column("Metric")
    svc_table.add_column("Value")
    
    services = results.get("services", {})
    active_services = sum(1 for s in services.values() if s.status == "active")
    svc_table.add_row("Total Services", str(len(services)))
    svc_table.add_row("Active Services", str(active_services))
    console.print(svc_table)

def display_security_analysis(results: dict):
    """Display security analysis results."""
    console.print("\n[bold red]Security Analysis Report[/bold red]")
    
    # System Security
    sys_security = results.get("system_security", {})
    sys_panel = Panel.fit(
        "\n".join(f"{k}: {'✓' if v else '✗'}" for k, v in sys_security.items()),
        title="System Security"
    )
    console.print(sys_panel)
    
    # Package Security
    pkg_security = results.get("package_security", {})
    verified_packages = sum(1 for v in pkg_security.values() if v)
    total_packages = len(pkg_security)
    
    pkg_panel = Panel.fit(
        f"Verified Packages: {verified_packages}/{total_packages}\n"
        f"Verification Rate: {(verified_packages/total_packages)*100:.1f}%",
        title="Package Security"
    )
    console.print(pkg_panel)
    
    # Service Security
    svc_security = results.get("service_security", {})
    svc_table = Table(title="Service Security")
    svc_table.add_column("Service")
    svc_table.add_column("Security Score")
    
    for service, checks in svc_security.items():
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        score = f"{(passed_checks/total_checks)*100:.1f}%"
        svc_table.add_row(service, score)
    
    console.print(svc_table)

def save_results(results: dict, filepath: str, format: str):
    """Save results to file."""
    if format == "json":
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    else:
        # Create text format output
        with open(filepath, 'w') as f:
            f.write("SecEnum System Enumeration Results\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            json.dump(results, f, indent=2, default=str)

def main():
    """Main entry point."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("An error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main()