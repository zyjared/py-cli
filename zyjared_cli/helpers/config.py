from pathlib import Path
import toml

__all__ = [
    'get_config',
    'save_config',
    'resolve_config',
    'CONFIG_PATH',
]

CONFIG_PATH = Path.cwd() / 'zycli.toml'


def get_config(config_path=CONFIG_PATH, *, cliname: str = None, group: str = None, ensure_exists: bool = False) -> None | dict:
    """
    获取指定路径的配置, 如果文件不存在则返回 `None`。
        - 如果 `ensure_exists` 为 `True`，则会创建文件，并返回空字典。
        - 可以进一步指定 `group` 和 `cliname` 项作为获取的键
    """
    if not config_path.exists():
        if ensure_exists:
            config = {}
            if group:
                config[group] = {}
                if cliname:
                    config[group][cliname] = {}
            elif cliname:
                config[cliname] = {}
            save_config(config_path, config=config)
            return config
        else:
            return None

    toml_string = config_path.read_text()
    config = toml.loads(toml_string)

    if group:
        config = config.get(group, {})

    if cliname:
        config = config.get(cliname, {})

    return config


def save_config(config_path=CONFIG_PATH, *, config: dict):
    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.write_text(toml.dumps(config))


def resolve_config(cliname: str = None, *, config_path=CONFIG_PATH, group: str = None, default_priority=True,  **kwargs):
    """
    获取指定路径配置的 `cliname` 项, 结果会合并 `**kwargs`。

    参数 `default_priority`:
      - 为 `True` 时，会优先使用非 `None` 的 `**kwargs` 值
      - 为 `False` 时，会优先使用非 `None` 的 `config` 值
    """
    config = get_config(config_path, cliname=cliname, group=group) or {}

    if not kwargs:
        pass
    elif default_priority:
        config = {**config, **{k: v for k, v in kwargs.items() if v is not None}}
    else:
        config = {**kwargs, **{k: v for k, v in config.items() if v is not None}}

    return config
