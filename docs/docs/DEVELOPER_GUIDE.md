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
| File                                |   Statements |   Missing |   Excluded | Coverage   |
|-------------------------------------|--------------|-----------|------------|------------|
| `corallium/__init__.py`             |            7 |         1 |          0 | 85.7%      |
| `corallium/file_helpers.py`         |          115 |        62 |          6 | 46.1%      |
| `corallium/log.py`                  |           59 |        14 |          0 | 76.3%      |
| `corallium/loggers/__init__.py`     |            0 |         0 |          0 | 100.0%     |
| `corallium/loggers/rich_printer.py` |           37 |        28 |          0 | 24.3%      |
| `corallium/loggers/styles.py`       |           24 |         3 |          0 | 87.5%      |
| `corallium/loggers/writer.py`       |            5 |         5 |          0 | 0.0%       |
| `corallium/pretty_process.py`       |           59 |        59 |          0 | 0.0%       |
| `corallium/scripts.py`              |            7 |         7 |          0 | 0.0%       |
| `corallium/shell.py`                |           33 |         2 |          0 | 93.9%      |
| `corallium/tomllib.py`              |            2 |         0 |          2 | 100.0%     |
| **Totals**                          |          348 |       181 |          8 | 48.0%      |

Generated on: 2023-02-25
<!-- {cte} -->
