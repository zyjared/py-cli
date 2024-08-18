from ...helpers.log import log_run, log_title
from ...helpers.command import command
from ._app import app, get_data, save_data, ENV_DIR, is_env_dir
from zyjared_color import bold
from typing import Annotated
from pathlib import Path
import typer


def _create_env(dir: str, *, env_dir: str = ENV_DIR) -> Path:
    dir = Path(dir).absolute()
    if is_env_dir(dir / env_dir):
        raise FileExistsError(f"{env_dir} already exists.")
    else:
        command(
            f'cd {dir} && python -m venv {env_dir}',
            silent=False,
            observe=False
        )
        return  dir / env_dir

def _add(alias: str, path: str, *, skip_venv: bool = False, env_dir: str = ENV_DIR):
    envs = get_data('ls')
    if envs is None:
        envs = []

    if any(v['alias'] == alias for v in envs):
        return {"error": f"{bold(alias)} already exists."}

    if skip_venv:
        if not is_env_dir(path):
            return {"error": f"{bold(path)} is not a valid venv path."}
        _venv_path = Path(path)
    else:
        _venv_path = _create_env(path, env_dir=env_dir)

    path = _venv_path.resolve().absolute().as_posix()
    envs.append(
        {"alias": alias, "path": path}
    )

    return {
        "code": save_data('ls', data=envs),
        "alias": alias,
        "path": path,
    }


@app.command()
def add(
    alias: Annotated[
        str,
        typer.Argument(
            help="Specify the venv alias.",
        )
    ],
    path: Annotated[
        str,
        typer.Argument(
            help="Specify the venv path.",
        )
    ],
    skip_venv: Annotated[
        bool,
        typer.Option(
            "--skip",
            show_default=False,
            help="Skip creating venv.",
        )
    ] = False,
    env_dir: Annotated[
        str,
        typer.Option(
            '--dir',
            help="Specify the venv directory name.",
        )
    ] = ENV_DIR
):
    """
    Add a venv.
    """
    log_title(cliname="venv add", tip="执行中...\n")
    log_run(
        lambda: _add(path=path, alias=alias,
                     skip_venv=skip_venv, env_dir=env_dir),
        cliname="env",
        result_alias="Added",
    )
