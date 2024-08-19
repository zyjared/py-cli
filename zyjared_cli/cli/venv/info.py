from ...helpers.log import log_run
from ._app import app, DATA_FILE

def _info():
    return {
        "数据文件": DATA_FILE
    }


@app.command()
def info():
    """
    显示一些信息
    """
    log_run(
        _info,
        cliname="env",
        result_alias="Info",
    )

