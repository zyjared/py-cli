from typing import Literal
from zyjared_color import Color, color, cyan, red, green, bold
import time
import sys

__all__ = [
    'log',
    'log_run'
]

UNITS = ['s', 'ms', 'us', 'ns']
PREDOT = Color(' · ').bold().cyan()
SEP = '  '

_COLORS = [
    'cyan',
    'blue',
    'magenta',
]
_COLOR_LEN = len(_COLORS)


def _color(text, i):
    return getattr(color(text), _COLORS[i % _COLOR_LEN])()


def _endow_unit(t: int, init_unit: Literal['s', 'ms', 'us', 'ns'] = 's', *, precision=2):
    i = UNITS.index(init_unit)

    for j in range(i, len(UNITS)):
        if t >= 1:
            break
        else:
            t = t * (1000 ** j)
            i = j

    if t > 1:
        msg = f'{round(t, precision)} {cyan(UNITS[i])}'
    else:
        msg = f'{'<1'} {cyan(UNITS[i])}'

    return {
        "time": t,
        "unit": UNITS[i],
        "msg": msg
    }


def measure_time(
        func,
        precision=2
):
    start = time.time()

    try:
        result = func()
        sucess = True
    except Exception as e:
        result = str(e)
        sucess = False

    end = time.time()

    endowed = _endow_unit(end - start, precision=precision)

    return {
        "sucess": sucess,
        "time": endowed['msg'],
        "result": result,
    }


def _log_list(ls: list, preblank: int = 2, prefix=PREDOT):
    if len(ls) == 0:
        sys.stdout.write(f'{SEP}{color("Empty List").yellow()}')
    for item in ls:
        sys.stdout.write(f'\n{prefix:>{preblank}}{item}')

    sys.stdout.flush()


def _log_dict(d: dict, preblank: int = 2, prefix=PREDOT, _cn=0):
    if len(d) == 0:
        return

    length = max([len(k) for k in d.keys()])
    for k, v in d.items():
        key = k if '\033[' in k else _color(k, _cn)
        sys.stdout.write(f'{" " * preblank}{key:<{length}}')
        if isinstance(v, list):
            _log_list(v, preblank + 4, prefix)
        elif isinstance(v, dict):
            sys.stdout.write('\n')
            _log_dict(v, preblank + 2, prefix, _cn + 1)
        elif isinstance(v, str) and not v:
            sys.stdout.write(f'{SEP}{v!r}\n')
        else:
            sys.stdout.write(f'{SEP}{v}\n')

    sys.stdout.flush()


def log_title(cliname: str = "tool", tip: Literal['success', 'fail', 'warning'] | str = ''):
    _pkgname = bold('ZYCLI').cyan()
    _cliname = bold(f'{cliname.capitalize()}').blue()
    if tip == 'success':
        _tip = Color(f'✓ {tip.capitalize()}').green().bold()
    elif tip == 'fail':
        _tip = Color(f'✗ {tip.capitalize()}').red().bold()
    elif tip == 'warning':
        _tip = Color(f'! {tip.capitalize()}').yellow().bold()
    else:
        _tip = color(tip).bold()

    # 📌 🎉 🚀 😕 😄 ✗ ✓
    print(f'\n📌 {_pkgname} {_cliname} {_tip}')


def log(
    content: str | list | dict | Color,
):
    if isinstance(content, list):
        _log_list(content, preblank=4, prefix=PREDOT)
    elif isinstance(content, dict):
        _log_dict(content, preblank=2, prefix=PREDOT)
    else:
        sys.stdout.write(f'{content}')
        sys.stdout.flush()


def log_run(func, *, precision=2, cliname="tool", result_alias="Result", show_title=True):
    res = measure_time(func, precision)

    status = None
    if show_title:
        status = 'success'
        if not res['sucess']:
            status = 'fail'
        elif (isinstance(res['result'], dict) and 'error' in res['result']):
            status = 'fail'
            v = res['result']["error"]
            del res['result']["error"]
            res['result'][f'{red("ERROR")}'] = v
        log_title(cliname, tip=status)

    _time = 'Time'
    _result = f'{result_alias}'

    if status == 'success':
        _time = green(_time)
        _result = green(_result)
    elif status == 'fail':
        _time = red(_time).red()
        _result = red(_result).red()

    log({
        f'{_time}': res['time'],
        f'{_result}': res['result'],
    })
