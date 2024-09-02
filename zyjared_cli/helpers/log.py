from typing import Literal
from zyjared_color import Color, color, red, green, bold, zprint
from ..utils.time_unit import endow_time_unit
import time

__all__ = [
    'log',
    'log_run'
]


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

    endowed = endow_time_unit(end - start, precision=precision)

    return {
        "sucess": sucess,
        "time": endowed,
        "result": result,
    }



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
    zprint(content, blank=2)

def log_run(func, *, precision=2, cliname="tool", result_alias="Result", show_title=True):
    res = measure_time(func, precision)

    status = None
    if show_title:
        status = 'success'
        if not res['sucess']:
            status = 'fail'
        elif isinstance(res['result'], dict) and ('error' in res['result'] or '错误' in res['result']):
            status = 'fail'
            err_key = '错误' if '错误' in res['result'] else 'error'
            v = res['result'][err_key]
            del res['result'][err_key]
            res['result'][f'{red(err_key)}'] = v
        log_title(cliname, tip=status)

    _time = 'Time'
    _result = f'{result_alias}'

    if status == 'success':
        _time = green(_time)
        _result = green(_result)
    elif status == 'fail':
        _time = red(_time).red()
        _result = red(_result).red()

    zprint({
        f'{_time}': res['time'],
        f'{_result}': res['result'],
    })
