from ...helpers.log import log_run
from ._app import app, get_data, is_env_dir
from zyjared_color import bold
from pathlib import Path
from typing import Annotated
from pathlib import Path
import pyperclip
import typer
import os


def _trigger(path: str):
    try:
        trigger = (Path(os.path.relpath(path, os.getcwd())) /
                   'Scripts' / 'activate').as_posix()
    except:
        cur_dir = Path.cwd().absolute().as_posix()
        env_dir = Path(path).absolute().as_posix()
        trigger = f"cd {env_dir} && Scripts/activate && cd {cur_dir}"

    pyperclip.copy(trigger)
    return trigger


def _activate(alias: str):
    """
    仅 windows
    """
    envs = get_data('ls')
    if envs is None:
        return {"error": "No venvs found."}

    target = None
    for v in envs:
        if v['alias'] == alias:
            target = v
            break

    if target is None:
        return {"error": f"{bold(alias)} not found."}
    elif not is_env_dir(target['path']):
        return {"warning": f"{bold(alias)} is not a venv."}

    trigger = _trigger(target['path'])

    return {
        "alias": target['alias'],
        "path": target['path'],
        "activate": f'{trigger}',
        "status": f'{bold('Copied!').green()}'
    }


@app.command()
def activate(
    alias: Annotated[
        str,
        typer.Argument(
            help="Specify the venv alias.",
        )
    ]
):
    """
    Activate a env.
    """
    log_run(
        lambda: _activate(alias),
        cliname="env",
        result_alias="Activated",
    )


@app.command()
def run(
    alias: Annotated[
        str,
        typer.Argument(
            help="Specify the venv alias.",
        )
    ]
):
    """
    An alias for activate.
    """
    log_run(
        lambda: _activate(alias),
        cliname="env",
        result_alias="Activated",
    )
