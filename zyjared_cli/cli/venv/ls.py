from ...helpers.log import log_run
from ._app import app, get_data
from pathlib import Path
import os


def _ls():
    venvs = get_data('ls')
    if venvs is None:
        return []

    res = {}
    for v in venvs:
        res[v['alias']] = {
            'path': v['path'],
            'activate': (Path(os.path.relpath(v['path'], os.getcwd())) / 'Scripts' / 'activate').as_posix()
        }

    return res


@app.command()
def ls():
    """
    List all venvs.
    """
    log_run(
        _ls,
        cliname="env",
        result_alias="Venvs",
    )