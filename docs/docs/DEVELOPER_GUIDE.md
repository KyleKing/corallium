# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/corallium.git
cd corallium
poetry install --sync
poetry run calcipy-pack pack.install-extras

# See the available tasks
poetry run calcipy
# Or use a local 'run' file (so that 'calcipy' can be extended)
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint.fix test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi or PyPi respectively

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

./run main pack.publish --to-test-pypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
./run release

# Or for a pre-release
./run release --suffix=rc
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                      | Statements | Missing | Excluded | Coverage |
|-----------------------------------------------------------|------------|---------|----------|----------|
| `corallium/__init__.py`                                   | 4          | 0       | 0        | 100.0%   |
| `corallium/_runtime_type_check_setup.py`                  | 14         | 0       | 33       | 100.0%   |
| `corallium/file_helpers.py`                               | 101        | 41      | 11       | 55.6%    |
| `corallium/log.py`                                        | 47         | 1       | 0        | 94.3%    |
| `corallium/loggers/__init__.py`                           | 0          | 0       | 0        | 100.0%   |
| `corallium/loggers/plain_printer.py`                      | 5          | 0       | 0        | 100.0%   |
| `corallium/loggers/rich_printer.py`                       | 37         | 11      | 0        | 62.7%    |
| `corallium/loggers/structlog_logger/__init__.py`          | 3          | 0       | 3        | 100.0%   |
| `corallium/loggers/structlog_logger/_structlog_logger.py` | 8          | 0       | 0        | 100.0%   |
| `corallium/loggers/styles.py`                             | 32         | 4       | 0        | 80.0%    |
| `corallium/pretty_process.py`                             | 55         | 55      | 0        | 0.0%     |
| `corallium/shell.py`                                      | 42         | 3       | 0        | 91.1%    |
| `corallium/tomllib.py`                                    | 3          | 0       | 2        | 100.0%   |
| **Totals**                                                | 351        | 115     | 49       | 62.7%    |

Generated on: 2024-11-07
<!-- {cte} -->
