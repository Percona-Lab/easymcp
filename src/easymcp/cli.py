"""easyMCP CLI - scaffold production-ready MCP server projects."""

import sys
from pathlib import Path

import click

from easymcp import __version__
from easymcp.prompts import run_prompts, c, info, error, BOLD
from easymcp.scaffold import scaffold


@click.group()
@click.version_option(__version__, prog_name="easymcp")
def main():
    """easyMCP - Scaffold production-ready MCP servers with polished installers."""
    pass


@main.command()
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Output directory (defaults to ./<project-slug>)",
)
def init(output: str | None):
    """Create a new MCP server project interactively."""
    try:
        config = run_prompts()
    except (KeyboardInterrupt, SystemExit):
        print()
        raise SystemExit(1)

    output_dir = Path(output) if output else Path.cwd() / config["project_slug"]
    output_dir = output_dir.resolve()

    if output_dir.exists() and any(output_dir.iterdir()):
        error(f"Directory {output_dir} already exists and is not empty.")
        raise SystemExit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    scaffold(config, output_dir)


if __name__ == "__main__":
    main()
