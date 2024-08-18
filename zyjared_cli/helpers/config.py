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
    获取指定路径的配置, 如果文件不存在则返回 `None`,否则返回 `dict`。
    可以进一步指定 `cli` 项。
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


def resolve_config(cliname: str = None, *, group: str = None, config_path=CONFIG_PATH, **kwargs):
    """
    获取指定路径配置的 `cli` 项, 可传入默认值 `**kwargs`。
    """
    config = get_config(config_path, cliname=cliname, group=group) or {}
    return {**kwargs, **config}


def prefer_specified_config(cliname: str = None, *, group: str = None, config_path=CONFIG_PATH, **kwargs):
    """
    获取指定路径配置的 `cli` 项, 优先使用 `**kwargs` 为真的值。
    """
    config = resolve_config(
        cliname=cliname, config_path=config_path, group=group)
    for k, v in kwargs.items():
        if v is not None and k in config:
            config[k] = v
    return config
