# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/corallium.git
cd corallium
uv sync --all-extras

# See the available tasks
uv run calcipy
# Or use a local 'run' file (so that 'calcipy' can be extended)
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint.fix test
```

### Maintenance

Dependency upgrades can be accomplished with:

```sh
uv lock --upgrade
uv sync --all-extras
```

## Publishing

Publishing is automated via GitHub Actions using PyPI Trusted Publishing. Tag creation triggers automated publishing.

```sh
./run release              # Bumps version, creates tag, pushes → triggers publish
./run release --suffix=rc  # For pre-releases
```

### Initial Setup

One-time setup to enable PyPI Trusted Publishing:

**Configure GitHub Environments**

Repository Settings → Environments:
- Create `testpypi` environment (no protection rules)
- Create `pypi` environment with "Required reviewers" enabled

**Register Trusted Publishers**

TestPyPI: https://test.pypi.org/manage/account/publishing/
- PyPI Project Name: `corallium`
- Owner: `kyleking`
- Repository: `corallium`
- Workflow: `publish.yml`
- Environment: `testpypi`

PyPI: https://pypi.org/manage/project/corallium/settings/publishing/
- Owner: `kyleking`
- Repository: `corallium`
- Workflow: `publish.yml`
- Environment: `pypi`

### Manual Publishing

For emergency manual publish:

```sh
export UV_PUBLISH_TOKEN=pypi-...
uv build
uv publish
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                      | Statements | Missing | Excluded | Coverage |
|-----------------------------------------------------------|-----------:|--------:|---------:|---------:|
| `corallium/__init__.py`                                   | 4          | 0       | 0        | 100.0%   |
| `corallium/_runtime_type_check_setup.py`                  | 13         | 0       | 37       | 100.0%   |
| `corallium/file_helpers.py`                               | 160        | 41      | 11       | 70.2%    |
| `corallium/log.py`                                        | 47         | 1       | 0        | 96.1%    |
| `corallium/loggers/__init__.py`                           | 0          | 0       | 0        | 100.0%   |
| `corallium/loggers/plain_printer.py`                      | 5          | 0       | 0        | 100.0%   |
| `corallium/loggers/rich_printer.py`                       | 37         | 27      | 0        | 19.6%    |
| `corallium/loggers/structlog_logger/__init__.py`          | 3          | 0       | 3        | 100.0%   |
| `corallium/loggers/structlog_logger/_structlog_logger.py` | 8          | 0       | 0        | 100.0%   |
| `corallium/loggers/styles.py`                             | 32         | 5       | 0        | 75.0%    |
| `corallium/pretty_process.py`                             | 58         | 58      | 0        | 0.0%     |
| `corallium/shell.py`                                      | 57         | 7       | 0        | 84.4%    |
| `corallium/tomllib.py`                                    | 3          | 0       | 2        | 100.0%   |
| **Totals**                                                | 427        | 139     | 53       | 62.7%    |

Generated on: 2026-01-23
<!-- {cte} -->
