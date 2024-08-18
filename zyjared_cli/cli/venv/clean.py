from ...helpers.log import log_run
from ._app import app, get_data, save_data, is_env_dir
from zyjared_color import bold
from pathlib import Path


def _clean():
    venvs = get_data('ls')
    if venvs is None:
        return {"error": "No venvs found."}

    removed = []
    dirs_exits = []
    for v in venvs:
        if is_env_dir(v["path"]):
            dirs_exits.append(v)
        else:
            removed.append(f'{bold(v["alias"])}: {v["path"]}')

    save_data('ls', data=removed)
    code = save_data('ls', data=dirs_exits)

    return {"code": code, "count": len(removed), "Removed": removed}


@app.command()
def clean():
    """
    Clean up venvs that don't have activate script.
    """
    log_run(
        lambda: _clean(),
        cliname="env",
        result_alias="Cleaned",
    )
