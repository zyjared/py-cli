from pathlib import Path
from typing import Literal
from zyjared_color import color
import toml

__all__ = [
    "version",
    "save_version",

    'load_version',
    'dump_version',

    "handle_version",
    "compare_version",
    "compare_dic_version",

    "PRE_MODE",
    "MODE",

    "pre_version",
    "mode_version",
]

_MODE = Literal['major', 'minor', 'patch', ]
_PREMODE = Literal['alpha', 'beta', 'rc', 'dev']
_INDEX = Literal[0, 1, 2, 4]
INDEX = [0, 1, 2, 4]

PYPROJECT_PATH = Path('pyproject.toml')
PRE_MODE = ['alpha', 'beta', 'rc', 'dev']
MODE = ['major', 'minor', 'patch']


def _read(p=PYPROJECT_PATH):
    if not p.exists():
        raise FileNotFoundError(f'Can not find {p}.')
    return toml.loads(p.read_text())


def _write(config, p=PYPROJECT_PATH):
    p.write_text(toml.dumps(config))


def load_version(v: str | list):
    if isinstance(v, list):
        return v

    ls = v.split('.')
    if '-' in ls[2]:
        _ls = ls[2].split('-')
        ls[2] = _ls[0]
        ls.insert(3, _ls[1])

    return ls


def dump_version(v: str | list):
    if isinstance(v, str):
        return v

    if len(v) < 4:
        return '.'.join(v)

    return '.'.join(v[:3]) + '-' + '.'.join(v[3:])


def _update_version(v: str | list, *, index: _INDEX, down: bool = False):
    _version: list[str] = load_version(v)
    if down:
        if _version[index] == '0':
            raise ValueError(f'Can not down {index} in {v}.')
        _version[index] = str(int(_version[index]) - 1)
    else:
        _version[index] = str(int(_version[index]) + 1)

    i = INDEX.index(index)
    _len = 3 if len(_version) < 4 else 4
    for j in range(i+1, _len):
        _version[j] = '0'
    return _version


def _up(v: str | list, index: _INDEX):
    return _update_version(v, index=index)


def _down(v: str | list, index: _INDEX):
    return _update_version(v, index=index, down=True)


def version(*, return_str: bool = False, config: dict = None):
    config = _read() if config is None else config
    try:
        v: str = config['tool']['poetry']['version']
        if return_str:
            return v
        return load_version(v)
    except KeyError:
        raise ValueError(
            'Can not find version in pyproject.toml. [tool.poetry.version]')


def save_version(v: str | list, *, config: dict = None, path=PYPROJECT_PATH):
    config = _read() if config is None else config
    config['tool']['poetry']['version'] = dump_version(v)
    _write(config, p=path)


def mode_version(mode: _MODE, *, down: bool = False, save: bool = False, save_path=PYPROJECT_PATH):
    index = MODE.index(mode)
    config = _read()
    _old: list = version(config=config)
    v: list = [i for i in _old]
    v = _down(v, index=index) if down else _up(v, index=index)
    v = v[:3]
    if save:
        save_version(v, config=config, path=save_path)

    return {
        "old": _old,
        "now": v,
    }


def pre_version(pre_mode: _PREMODE, *, down: bool = False, save: bool = False, save_path=PYPROJECT_PATH):
    config = _read()
    _old: list = version(config=config)
    v: list = [i for i in _old]
    if len(v) < 4:
        v.extend([pre_mode, '1'])
    elif v[3] != pre_mode:
        v[3] = pre_mode
        v[4] = '1'
    else:
        if down:
            v = _down(v, index=4)
            if v[4] == '0':
                v = v[:3]
        else:
            v = _up(v, index=4)
    if save:
        save_version(v, config=config, path=save_path)

    return {
        "old": _old,
        "now": v,
    }


def _result(dic: dict[str, list | str]):
    old = [i for i in dic['old']] if isinstance(
        dic['old'], list) else load_version(dic['old'])
    now = [i for i in dic['now']] if isinstance(
        dic['now'], list) else load_version(dic['now'])

    _len_old = len(old)
    _len_now = len(now)
    _min = min(_len_old, _len_now)

    def _log(t): return str(color(t).red())

    for i in range(_min):
        if old[i] != now[i]:
            old[i] = _log(old[i])
            now[i] = _log(now[i])

    if _len_old > _len_now:
        for i in range(_len_now, _len_old):
            old[i] = _log(old[i])
    elif _len_old < _len_now:
        for i in range(_len_old, _len_now):
            now[i] = _log(now[i])
    else:
        pass

    return {
        'old': dump_version(old),
        'now': dump_version(now),
    }


compare_dic_version = _result


def compare_version(old: list | str, now: list | str):
    return _result({'old': old, 'now': now})


def handle_version(mode: _MODE | _PREMODE, *, down: bool = False, save: bool = False, save_path=PYPROJECT_PATH):
    if mode in MODE:
        return mode_version(mode, down=down, save=save, save_path=save_path)
    elif mode in PRE_MODE:
        return pre_version(mode, down=down, save=save, save_path=save_path)
    else:
        raise ValueError(f'Can not handle {mode}.')
