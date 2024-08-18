from typing import List, Annotated
import typer
import os
import fnmatch
from .app import app
from ..helpers.log import log_run
from ..helpers.config import prefer_specified_config
import shutil

__all__ = [
    'clean'
]


def _rmdir(path: str):
    shutil.rmtree(path)


def _fpath(filename: str):
    """
    - 将分隔符统一为 /
    - 如果是文件夹, 以 / 结尾
    - 以 / 开头
    """
    if os.path.isdir(filename) and not filename.endswith('/'):
        filename += '/'
    pathname = '/'.join(filename.split(os.sep))
    if pathname.startswith('/'):
        return pathname
    return pathname[1:] if pathname.startswith('./') else '/' + pathname


def _fpattern(pattern: str):
    """
    以下符号作为首个符号:
      - `*`
      - `**`
      - `/`
    """
    if pattern.startswith('/') or pattern.startswith('*'):
        return pattern
    else:
        return '**/' + pattern


def _match(filename: str, patterns: list[str]):
    """
    判断文件名是否在给定的 patterns 中,
    filemame 和 pattern 应已被 _fpath 和 _fpattern 处理
    """
    for pattern in patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def _sep_patterns(patterns: list[str]):
    include = []
    exclude = []
    for p in patterns:
        if p.startswith('!'):
            exclude.append(_fpattern(p[1:]))
        else:
            include.append(_fpattern(p))
    return include, exclude


def _clean0(filename: str, exclude: list[str]):
    """
    给定排除列表的 pattern, 如果文件名不在排除列表中, 则删除文件
    """
    if not _match(_fpath(filename), exclude):
        if os.path.isfile(filename):
            os.remove(filename)
        else:
            for child in os.listdir(filename):
                _clean0(os.path.join(filename, child), exclude)
            try:
                os.rmdir(filename)
            except OSError:
                pass
    if os.path.isdir(filename):
        for child in os.listdir(filename):
            _clean0(os.path.join(filename, child), exclude)


def _clean1(filename: str, include: list[str], exclude: list[str] = [], removed: list[str] = []):
    _filename = _fpath(filename)
    if _match(_filename, include) and not _match(_filename, exclude):
        if os.path.isfile(filename):
            os.remove(filename)
            removed.append(filename)
        else:
            try:
                if exclude:
                    for child in os.listdir(filename):
                        _clean0(os.path.join(filename, child), exclude)
                    os.rmdir(filename)
                    removed.append(filename)
                else:
                    _rmdir(filename)
                    removed.append(filename)
            except OSError:
                removed.append(f'(skipped) {filename}')

    if os.path.isdir(filename):
        for child in os.listdir(filename):
            _clean1(os.path.join(filename, child), include, exclude, removed)

    return removed


def _clean(dirpath: str = None, patterns: list[str] = None):
    if not dirpath:
        return {'error': 'No directory specified.'}

    if not os.path.exists(dirpath):
        return {'error': f'Directory {dirpath} does not exist.'}
    if not patterns:
        return {'error': 'No patterns specified.'}
    include, exclude = _sep_patterns(patterns)
    return {
        'dirpath': dirpath,
        'removed': _clean1(dirpath, include, exclude)
    }


@app.command()
def clean(
    dirpath: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="Specify the directory to clean up.",
        )
    ] = None,
    pattern: Annotated[
        List[str],
        typer.Option(
            '-p',
            '--pattern',
            show_default=False,
            help="Specify the pattern to clean up.",
        )
    ] = None,
):
    """
    Clean up files in a directory with specified pattern.
    """

    config = prefer_specified_config(
        cliname='clean',
        dirpath=dirpath,
        pattern=pattern
    )

    log_run(
        lambda: _clean(
            config['dirpath'],
            config['pattern'],
        ),
        cliname='clean',
    )
