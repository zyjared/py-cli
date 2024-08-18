import typer
from importlib.metadata import version, PackageNotFoundError

app = typer.Typer()


def get_version() -> str:
    try:
        return version('zyjared_cli')
    except PackageNotFoundError:
        return 'unknown'


def version_callback(value: bool):
    if value:
        typer.echo(f'version: {get_version()}')
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version number and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    zyjared's tool.
    """
