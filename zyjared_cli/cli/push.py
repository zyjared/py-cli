from typing import Annotated
import typer
from .app import app
from ..helpers.version import dump_version, handle_version, compare_dic_version, version
from enum import Enum
import subprocess
from ..helpers.log import log, log_title
from zyjared_color import Color, bold, italic
import sys

__all__ = [
    'push'
]


class _V(str, Enum):
    patch = 'patch'
    minor = 'minor'
    major = 'major'
    alpha = 'alpha'
    beta = 'beta'
    rc = 'rc'
    dev = 'dev'


def _log(cmd: str, output: str | Color):
    sys.stdout.write(f'  {bold(">").green()} {cmd}\n')
    if isinstance(output, Color):
        sys.stdout.write(f'  {bold(".").cyan()} {output}\n')
    else:
        _outs = output.split('\n')
        for _out in _outs:
            sys.stdout.write(f'  {bold(".").cyan()} {_out}\n')
    sys.stdout.flush()


def _subsystem(cmd: str, *, silent=False, observe=False):
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


def _system(silent=False, observe=False, *args):
    for arg in args:
        _subsystem(arg, silent=silent, observe=observe)
    return list(args)


def _push(message: str = None, *, amend=False, tag: _V = None, retag=False, silent=False, observe=False):
    result = {}

    v = version(return_str=True)

    if retag:
        _system(
            silent,
            observe,
            f'git tag -d v{v}',
            f'git push origin -d v{v}',
        )

    if tag:
        up = handle_version(mode=tag.value, down=False, save=(not observe))
        v = dump_version(up['now'])
        result["tag"] = compare_dic_version(up)

        if not silent or observe:
            _log(
                f'zycli version {tag.value}',
                f'{italic("<observe> ").bright_black() if observe else ""}{
                    dump_version(up['old'])} -> {dump_version(up['now'])}',
            )

    _system(
        silent,
        observe,
        'git add .',
        f'git commit{"" if not amend else " --amend"} -m "{message}"',
        f'git push origin main{"" if not amend else " --force"}',
    )

    if tag or retag:
        _system(
            silent,
            observe,
            f'git tag v{v}',
            f'git push origin v{v}',
        )

    result['version'] = v

    return result


@app.command()
def push(
    message: Annotated[
        str,
        typer.Option(
            "-m",
            "--message",
            show_default=False,
            help="Specify the commit message.",
        ),
    ] = None,
    amend: Annotated[
        bool,
        typer.Option(
            "--amend",
            show_default=False,
            help="Amend the commit.",
        )
    ] = False,
    tag: Annotated[
        _V,
        typer.Option(
            "--tag",
            show_default=False,
            help="Push the latest tag.",
        )
    ] = None,
    retag: Annotated[
        bool,
        typer.Option(
            "--retag",
            show_default=False,
            help="Retag the latest tag.",
        )
    ] = False,
    silent: Annotated[
        bool,
        typer.Option(
            "--silent",
            show_default=False,
            help="Show the command.",
        )
    ] = False,
    observe: Annotated[
        bool,
        typer.Option(
            "--observe",
            show_default=False,
            help="Observe the command. Only used in debug mode.",
        )
    ] = False,
):
    """
    Push to the repo.
    """
    log_title(cliname='push')
    try:
        result = _push(message, amend=amend, tag=tag,
                       retag=retag, silent=silent, observe=observe)
        status = bold('SUCCESS').green()
    except Exception as e:
        result = {'error': str(e)}
        status = bold('FAIL').red()
    finally:
        log({
            'Status': status,
            'Result': result
        })
