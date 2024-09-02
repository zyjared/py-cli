from typing import Literal
from zyjared_color import Color, cyan

__all__ = [
    "endow_time_unit"
]

UNITS = ['s', 'ms', 'us', 'ns']


def endow_time_unit(t: int, *, init_unit: Literal['s', 'ms', 'us', 'ns'] = 's', precision=2, color: Color = cyan):
    i = UNITS.index(init_unit)

    for j in range(i + 1, len(UNITS)):
        if t >= 1:
            break
        else:
            t *= 1000
            i = j

    if t > 1:
        return f'{t:.{precision}f} {color(UNITS[i])}'
    else:
        return f'{'<1'} {color(UNITS[i])}'


if __name__ == '__main__':
    print(endow_time_unit(0.0001, init_unit='ms', precision=3))
