from zyjared_color import Color, bold, italic
import subprocess
import sys

__all__ = [
    'command',
    'commands',
]


def _log(cmd: str, output: str | Color):
    sys.stdout.write(f'  {bold(">").green()} {cmd}\n')
    sys.stdout.write(f'  {bold(".").cyan()} {output}\n')
    sys.stdout.flush()


def command(cmd: str, *, silent=False, observe=False):
    """
    - `silent`: 静默执行
    - `observe`: 打印命令但不执行
    """
    try:
        if observe:
            result = italic('<observe>').bright_black()
        else:
            result = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        if observe or not silent:
            _log(cmd, result)
        return result
    except subprocess.CalledProcessError as e:
        raise Exception(f'command error: {cmd}\nError message: {e.output}')


def commands(silent=False, observe=False, *args):
    """
    - `silent`: 静默执行
    - `observe`: 打印命令但不执行
    """
    for arg in args:
        command(arg, silent=silent, observe=observe)
    return list(args)
