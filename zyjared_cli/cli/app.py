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
        "-v",
        "--version",
        help="显示版本号",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    zyjared 自用的命令行工具
    """
