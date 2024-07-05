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
| `corallium/_runtime_type_check_setup.py`                  | 13         | 0       | 28       | 100.0%   |
| `corallium/file_helpers.py`                               | 94         | 40      | 12       | 53.2%    |
| `corallium/log.py`                                        | 46         | 1       | 0        | 94.2%    |
| `corallium/loggers/__init__.py`                           | 0          | 0       | 0        | 100.0%   |
| `corallium/loggers/plain_printer.py`                      | 4          | 0       | 0        | 100.0%   |
| `corallium/loggers/rich_printer.py`                       | 36         | 28      | 0        | 16.0%    |
| `corallium/loggers/structlog_logger/__init__.py`          | 3          | 0       | 3        | 100.0%   |
| `corallium/loggers/structlog_logger/_structlog_logger.py` | 7          | 0       | 0        | 100.0%   |
| `corallium/loggers/styles.py`                             | 27         | 5       | 0        | 72.7%    |
| `corallium/pretty_process.py`                             | 53         | 53      | 0        | 0.0%     |
| `corallium/shell.py`                                      | 41         | 4       | 0        | 87.3%    |
| `corallium/tomllib.py`                                    | 3          | 0       | 2        | 100.0%   |
| **Totals**                                                | 331        | 131     | 45       | 55.1%    |

Generated on: 2024-07-05
<!-- {cte} -->
