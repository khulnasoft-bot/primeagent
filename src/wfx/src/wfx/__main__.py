"""WFX CLI entry point."""

import typer

from wfx.cli.commands import serve_command
from wfx.cli.run import run

app = typer.Typer(
    name="wfx",
    help="wfx - Primeagent Executor",
    add_completion=False,
)

# Add commands
app.command(name="serve", help="Serve a flow as an API", no_args_is_help=True)(serve_command)
app.command(name="run", help="Run a flow directly", no_args_is_help=True)(run)


def main():
    """Main entry point for the WFX CLI."""
    app()


if __name__ == "__main__":
    main()
