from ...helpers.log import log_run, log_title
from ...helpers.command import command
from ._app import app, get_data, save_data, ENV_DIR, is_env_dir
from zyjared_color import bold
from typing import Annotated
from pathlib import Path
import typer
import os


def _create_env(dir: str, *, env_dir: str = ENV_DIR) -> Path:
    dir = Path(dir).absolute()
    _env = dir / env_dir
    if os.path.exists(str(_env)):
        if is_env_dir(_env):
            raise FileExistsError(f"{_env} 已经存在，并且是一个虚拟环境目录。")
        raise FileExistsError(f"{dir} 已经存在。")
    else:
        command(
            f'cd {dir} && python -m venv {env_dir}',
            silent=False,
            observe=False
        )
        return _env


def _add(alias: str, path: str, *, skip_venv: bool = False, env_dir: str = ENV_DIR):
    envs = get_data('ls')
    if envs is None:
        envs = []

    if any(v['alias'] == alias for v in envs):
        return {"error": f"{bold(alias)} 已经存在。"}

    if skip_venv:
        if not is_env_dir(path):
            return {"error": f"{bold(path).red()} 不是一个有效的虚拟环境路径。"}
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
            help="虚拟环境的别名。",
        )
    ],
    path: Annotated[
        str,
        typer.Argument(
            help="在该路径下创建虚拟环境。",
        )
    ],
    skip_venv: Annotated[
        bool,
        typer.Option(
            "--skip",
            show_default=False,
            help="不创建虚拟环境，仅将别名和路径写入配置。",
        )
    ] = False,
    env_dir: Annotated[
        str,
        typer.Option(
            '--dir',
            help="虚拟环境目录名。",
        )
    ] = ENV_DIR
):
    """
    添加一个虚拟环境
    """
    log_title(cliname="venv add", tip="执行中...\n")
    log_run(
        lambda: _add(alias=alias, path=path,
                     skip_venv=skip_venv, env_dir=env_dir),
        cliname="env",
        result_alias="Added",
    )
