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

PyPI: https://pypi.org/manage/project/corallium/settings/publishing/
- Owner: `kyleking`
- Repository: `corallium`
- Workflow: `publish.yml`
- Environment: `pypi`
    - Or environment `testpypi` (for [TestPyPI](https://test.pypi.org/manage/account/publishing))

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
| `corallium/__init__.py`                                   | 6          | 0       | 0        | 100.0%   |
| `corallium/_runtime_type_check_setup.py`                  | 13         | 0       | 37       | 100.0%   |
| `corallium/can_skip.py`                                   | 14         | 0       | 0        | 100.0%   |
| `corallium/code_tag_collector/__init__.py`                | 6          | 3       | 0        | 50.0%    |
| `corallium/code_tag_collector/_collector.py`              | 133        | 30      | 0        | 73.1%    |
| `corallium/file_helpers.py`                               | 170        | 42      | 11       | 71.3%    |
| `corallium/file_search.py`                                | 52         | 2       | 2        | 97.2%    |
| `corallium/log.py`                                        | 47         | 1       | 0        | 96.1%    |
| `corallium/loggers/__init__.py`                           | 0          | 0       | 0        | 100.0%   |
| `corallium/loggers/plain_printer.py`                      | 5          | 0       | 0        | 100.0%   |
| `corallium/loggers/rich_printer.py`                       | 37         | 8       | 0        | 72.5%    |
| `corallium/loggers/structlog_logger/__init__.py`          | 3          | 0       | 3        | 100.0%   |
| `corallium/loggers/structlog_logger/_structlog_logger.py` | 8          | 0       | 0        | 100.0%   |
| `corallium/loggers/styles.py`                             | 32         | 3       | 0        | 86.1%    |
| `corallium/markup_table.py`                               | 31         | 0       | 0        | 100.0%   |
| `corallium/pretty_process.py`                             | 58         | 13      | 0        | 77.8%    |
| `corallium/shell.py`                                      | 69         | 13      | 0        | 74.7%    |
| `corallium/sync_dependencies.py`                          | 155        | 8       | 0        | 90.6%    |
| `corallium/tomllib.py`                                    | 4          | 0       | 2        | 100.0%   |
| `corallium/vcs/__init__.py`                               | 6          | 0       | 0        | 100.0%   |
| `corallium/vcs/_forge.py`                                 | 50         | 2       | 0        | 94.9%    |
| `corallium/vcs/_git_commands.py`                          | 20         | 0       | 0        | 100.0%   |
| `corallium/vcs/_jj_commands.py`                           | 23         | 0       | 0        | 100.0%   |
| `corallium/vcs/_repo.py`                                  | 67         | 2       | 0        | 94.6%    |
| `corallium/vcs/_types.py`                                 | 21         | 0       | 0        | 100.0%   |
| **Totals**                                                | 1030       | 127     | 55       | 84.7%    |

Generated on: 2026-01-30
<!-- {cte} -->
