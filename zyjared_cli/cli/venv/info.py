from ...helpers.log import log_run
from ._app import app, DATA_FILE

def _info():
    return {
        "file": DATA_FILE
    }


@app.command()
def info():
    """
    Show some information.
    """
    log_run(
        _info,
        cliname="env",
        result_alias="Info",
    )

