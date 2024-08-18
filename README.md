# zyjared-cli

## Usage

```sh
pip install zyjared-cli
```

```sh
zycli --help
```

## List

### config

```sh
zycli config --help

# zycli config [cli name]
# zycli config [group.]
# zycli config [group.name]
```

```sh
zycli config --init

# zycli config [cli name] --init
# zycli config clean --init
```

example:

```sh
zycli config clean --init
```

`zycli.toml` will be created if not exists:

```toml
[clean]
dirpath = ""
pattern = []
```

### clean

```sh
zycli clean --help
```

example:

```sh
zycli clean test -p "*.py" -p "!folder/*.py"
```

or use config file:

```sh
zycli clean
```

```toml
# zycli.toml
[clean]
dirpath = "test"
pattern = ["*.py", "!folder/*.py"]
```

### version

```sh
zycli version --help
```

example:

```sh
zycli version patch [--down]
```

- `patch`
- `minor`
- `major`
- `alpha`
- `beta`
- `rc`
- `dev`

### push

```sh
zycli push --help
```

example:

```sh
zycli push -m "test" --tag patch
```

```sh
zycli push -m "test" --tag patch --amend --retag
```
