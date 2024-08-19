from ...helpers.log import log_run
from ._app import app, get_data, save_data, is_env_dir
from zyjared_color import bold
from typing import Annotated
from pathlib import Path
import typer
import shutil


def _remove(alias: str):
    venvs = get_data('ls')
    if venvs is None:
        return {"error": "虚拟环境的数据不存在。"}

    _venvs = []
    _removed = None
    for v in venvs:
        if v['alias'] == alias:
            _removed = v
        else:
            _venvs.append(v)

    if _removed is None:
        return {"error": f"Venv {bold(alias)} not found."}

    if is_env_dir(_removed['path']):
        shutil.rmtree(_removed['path'])

    return {
        "code": save_data('ls', data=_venvs),
        "alias": _removed['alias'],
        "path": _removed['path'],
    }


@app.command()
def remove(
    alias: Annotated[
        str,
        typer.Argument(
            help="虚拟环境的别名。",
        )
    ]
):
    """
    删除虚拟环境
    """
    log_run(
        lambda: _remove(alias),
        cliname="env",
        result_alias="Removed",
    )
