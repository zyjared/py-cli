from ...helpers.config import get_config, save_config
from pathlib import Path
from typing import Any, Literal
import typer

app = typer.Typer()

ENV_DIR = '.venv'
DATA_FILE = Path.home() / '.zycli.toml'
DATA_KEYS = {
    'ls': 'env',
}


_DATA_KEY = Literal['ls']


@app.callback()
def callback():
    """
    管理虚拟环境

    如果不是通过 add 创建的虚拟环境，不会出现在 `ls` 命令中, 可以通过 `add --skip` 来添加。
    """


def get_data(key: _DATA_KEY):
    config = get_config(
        DATA_FILE,
        cliname='venv'
    ) or {}

    if DATA_KEYS[key] not in config:
        return None

    return config[DATA_KEYS[key]]


def save_data(key: _DATA_KEY, *, data: Any):
    config = get_config(DATA_FILE, ensure_exists=True)

    if 'venv' not in config:
        config['venv'] = {}

    config['venv'][DATA_KEYS[key]] = data

    return save_config(DATA_FILE, config=config)


def is_env_dir(path: str | Path):
    if isinstance(path, str):
        path = Path(path)
    return (path / 'Scripts' / 'activate').exists()
