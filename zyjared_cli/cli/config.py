from typing import Annotated, Any
from zyjared_color import red, italic
import toml
import typer
import inspect
from .app import app
from ..helpers.log import log_run
from ..helpers.config import get_config, CONFIG_PATH

__all__ = [
    'config',
]


CLIS = [
    'clean'
]

DEFAULT = {
    'str': '',
    'list': [],
    'List': [],
    'dict': {},
    'Dict': {},
}


def _ignore(cliname: str, *, group: str = None):
    if group:
        return group not in CLIS
    return cliname not in CLIS


def _save(config, config_path=CONFIG_PATH):
    config_path.write_text(toml.dumps(config))


def _fcliname(cliname: str, *, color=True, group: str = None):
    text = f'{group}.{cliname}' if group else cliname
    if color:
        return f"{red('[')}{italic(text)}{red(']')}"
    else:
        return f'[{text}]'


def _func_params(func):
    signature = inspect.signature(func)
    parameters = signature.parameters
    return [
        {
            'name': name,
            'type': parameter.annotation,
            'default': parameter.default
        } for name, parameter in parameters.items()
    ]


def _func_param_default(param: list[dict[str, Any]]):
    if param['default'] is not inspect.Parameter.empty and param['default'] is not None:
        return param['default']

    if param['type'] in DEFAULT:
        return DEFAULT[param['type']]

    elif param['type'].__name__ == 'Annotated':
        _cname = param['type'].__args__[0].__name__
        if _cname in DEFAULT:
            return DEFAULT[_cname]
        return 'unknown type'

    return 'unknown type'


def _func_params_values(func):
    dic = {}
    for p in _func_params(func):
        dic[p['name']] = _func_param_default(p)
    return dic


def _typer_instance_command(instance: typer.Typer, *, command_name: str, group: str = None):
    if group:
        for c in instance.registered_groups:
            if c.name == group:
                return _typer_instance_command(c.typer_instance, command_name)
    else:
        for c in instance.registered_commands:
            if c.callback.__name__ == command_name:
                return c

    return None


def get_command_config(cliname: str, *, group: str = None):
    """
    从 app 中获取指定命令的配置
    """
    if _ignore(cliname, group=group):
        return None

    command = _typer_instance_command(app, cliname=cliname, group=group)

    if not command:
        return None

    return _func_params_values(command.callback)


def get_typer_instance_config(instance: typer.Typer, *, group: str = None, cover_config: dict = None):
    """
    从指定的 Typer 中获取所有命令的配置
    """
    dic = cover_config if cover_config is not None else {}

    for c in instance.registered_commands:
        _cname = c.callback.__name__
        if _cname in dic or _ignore(_cname, group=group):
            continue
        dic[_cname] = _func_params_values(c.callback)

    for c in instance.registered_groups:
        _info = get_typer_instance_config(c.typer_instance, group=c.name)
        if _info:
            dic[c.name] = _info

    return dic


def _formate_config(config: dict[str, Any], *, group: str = None):
    _cli = {}

    for k, v in config.items():
        _cli[str(_fcliname(k, group=group))] = v

    return _cli


def _config(cliname: str | None, *, group: str = None):
    """
    获取配置项
    """
    c = get_config() or {}

    if not group and not cliname:
        return _formate_config(c)

    elif group and not cliname:
        if group in c:
            return _formate_config(c[group], group=group)
        else:
            return {'错误': red(f"配置项[{group}]不存在。")}

    elif group:
        if group in c and cliname in c[group]:
            return c[group][cliname]
        else:
            return {'错误': red(f"配置项[{group}.{cliname}]不存在。")}

    else:
        if cliname in c:
            return c[cliname]
        else:
            return {'错误': red(f"配置项[{cliname}]不存在。")}


def _init(cliname: str | None, *, group: str = None):
    c = get_config(ensure_exists=True)

    if group and not cliname:
        for g in app.registered_groups:
            if g.name == group:
                _c = get_typer_instance_config(
                    g.typer_instance,
                    group=group,
                    cover_config=c.get(group, {}),
                )
                if _c:
                    c[group] = _c
                else:
                    return {'错误': red(f"配置项[{group}]不存在。")}
                break
    elif group:
        if group in c and cliname in c[group]:
            return {'错误': red(f"配置项[{group}.{cliname}]已存在。")}

        _dic = get_command_config(cliname, group=group)
        if _dic is None:
            return {'错误': f'未找到配置项[{group}.{cliname}]。'}

        if group in c:
            c[group][cliname] = _dic
        else:
            c[group] = {cliname: _dic}

    elif cliname:
        if cliname in c:
            return {'错误': red(f"配置项[{cliname}]已存在。")}

        _dic = get_command_config(cliname)
        if _dic is None:
            return {'错误': f'未找到配置项[{cliname}]。'}

        c[cliname] = _dic
    else:
        get_typer_instance_config(app, cover_config=c)

    _save(c)
    return _config(cliname, group=group)


def _split_cliname(cliname: str | None):
    """
    将 `cliname` 名拆分为 `group` 和 `cliname`
    """
    if cliname is None:
        return None, None
    elif '.' in cliname:
        return tuple(cliname.split('.', 1))
    else:
        return None, cliname


@app.command()
def config(
    cliname: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="命令名，不指定则为所有配置项。",
        ),
    ] = None,
    init: Annotated[
        bool,
        typer.Option(
            '-i',
            '--init',
            show_default=False,
            help="初始化配置文件。如果已存在配置项，则会跳过。",
        ),
    ] = False,
):
    """
    获取配置项，或初始化配置文件

    Example:

        $ zycli config

        $ zycli config --init

        $ zycli config clean

        $ zycli config clean --init
    """
    [group, cli] = _split_cliname(cliname)
    if init:
        log_run(
            lambda: _init(cli, group=group),
            cliname='config',
            result_alias='配置' +
                (_fcliname(f'{cli}', group=group, color=False)
                 if cli is not None else '')
        )
    else:
        log_run(
            lambda: _config(cli, group=group),
            cliname='config',
            result_alias='配置' if cli is None else _fcliname(
                cli, group=group, color=False),
        )
