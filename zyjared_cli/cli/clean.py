from typing import List, Annotated
import typer
import os
import fnmatch
from .app import app
from ..helpers.log import log_run
from ..helpers.config import resolve_config
from zyjared_color import bright_black
import shutil

gray = bright_black

__all__ = [
    'clean'
]

DEFAULT_IGNORE = [
    ''
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
    判断文件名是否和 patterns 中的规则匹配。

    filemame 和 patterns 应已被 _fpath 和 _fpattern 处理。
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
    删除匹配 exclude 中的规则的文件
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
    """
    删除匹配 include 中的规则但不匹配 exclude 中的规则的文件
    """
    _filename = _fpath(filename)
    if _match(_filename, exclude):
        return removed

    if _match(_filename, include):
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
                removed.append(f'{gray('<已忽略>')} {filename}')
    elif os.path.isdir(filename):
        for child in os.listdir(filename):
            _clean1(os.path.join(filename, child), include, exclude, removed)

    return removed


def _clean(dirpath: str = None, patterns: list[str] = None):
    if not dirpath:
        return {'错误': '未指定目录。'}

    if not os.path.exists(dirpath):
        return {'错误': f'目录 {dirpath} 不存在。'}
    if not patterns:
        return {'错误': '未指定清理规则。'}
    include, exclude = _sep_patterns(patterns)
    return {
        '目录': dirpath,
        '清理': _clean1(dirpath, include, exclude)
    }


@app.command()
def clean(
    dirpath: Annotated[
        str,
        typer.Argument(
            help="需要清理的目录。",
        )
    ] = None,
    pattern: Annotated[
        List[str],
        typer.Option(
            '-p',
            '--pattern',
            help="清理规则，支持通配符。",
        )
    ] = None,
):
    """
    根据清理规则清理目录下的文件
    """

    config = resolve_config(
        cliname='clean',
        default_priority=True,
        dirpath=dirpath,
        pattern=pattern
    )

    print(config)

    log_run(
        lambda: _clean(
            config['dirpath'],
            config['pattern'],
        ),
        cliname='clean',
    )
