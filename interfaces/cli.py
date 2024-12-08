"""Command-line interface for SecEnum."""

import click
from rich.console import Console
from rich.table import Table
from typing import Optional
import json
import logging

console = Console()
logger = logging.getLogger(__name__)

@click.group()
@click.option("--debug/--no-debug", default=False, help="Enable debug logging")
def cli(debug: bool):
    """SecEnum: Advanced System Software Enumeration & Security Assessment Tool"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)

@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "text"]), default="text")
def scan(output: Optional[str], format: str):
    """Perform system software enumeration."""
    console.print("[bold blue]Starting system enumeration...[/bold blue]")
    # Implementation to be added
    pass

@cli.command()
@click.option("--full/--quick", default=False, help="Perform full security assessment")
def assess(full: bool):
    """Perform security assessment."""
    console.print("[bold yellow]Starting security assessment...[/bold yellow]")
    # Implementation to be added
    pass

def main():
    """Main entry point."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("An error occurred")
        raise

if __name__ == "__main__":
    main()