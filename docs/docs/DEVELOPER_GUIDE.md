# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/corallium.git
cd corallium
poetry install --sync

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
| File                                                      |   Statements |   Missing |   Excluded | Coverage   |
|-----------------------------------------------------------|--------------|-----------|------------|------------|
| `corallium/__init__.py`                                   |           17 |         0 |         17 | 100.0%     |
| `corallium/file_helpers.py`                               |          113 |        32 |          6 | 61.7%      |
| `corallium/log.py`                                        |           59 |         1 |          0 | 94.4%      |
| `corallium/loggers/__init__.py`                           |            0 |         0 |          0 | 100.0%     |
| `corallium/loggers/plain_printer.py`                      |            6 |         0 |          0 | 100.0%     |
| `corallium/loggers/rich_printer.py`                       |           38 |         8 |          0 | 72.2%      |
| `corallium/loggers/structlog_logger/__init__.py`          |            2 |         0 |          3 | 100.0%     |
| `corallium/loggers/structlog_logger/_structlog_logger.py` |            9 |         0 |          0 | 100.0%     |
| `corallium/loggers/styles.py`                             |           23 |         0 |          0 | 96.3%      |
| `corallium/pretty_process.py`                             |           59 |        59 |          0 | 0.0%       |
| `corallium/shell.py`                                      |           44 |         3 |          0 | 91.9%      |
| `corallium/tomllib.py`                                    |            2 |         0 |          2 | 100.0%     |
| **Totals**                                                |          372 |       103 |         28 | 66.4%      |

Generated on: 2023-08-14
<!-- {cte} -->
