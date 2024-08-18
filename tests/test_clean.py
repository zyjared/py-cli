from pathlib import Path
from typer.testing import CliRunner
from zyjared_cli.main import app

runner = CliRunner()


def create_files(files=[f'{i}.py' for i in range(1, 3)]):

    test = Path.cwd() / 'test'
    if not test.exists():
        test.mkdir()

    for file in files:
        test.joinpath(file).touch()
        print(f'created {file}')


def test_app():

    create_files()

    result = runner.invoke(app, ['clean', 'test', '--pattern', '*.py'])
    assert result.exit_code == 0

    assert "1.py" in result.stdout
    assert "2.py" in result.stdout
