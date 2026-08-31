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

Publishing is automated via GitHub Actions using PyPI Trusted Publishing. Pushing the tag triggers it.

`./run release` stops at the local tag. Nothing reaches PyPI until you push, which keeps the irreversible step a deliberate one.

```sh
./run release                       # Bumps the version and tags it
./run release --suffix=rc           # For pre-releases
python -m commitizen changelog      # See the follow-up below; not yet automatic here
mv CHANGELOG.md docs/docs/CHANGELOG.md
git add docs/docs/CHANGELOG.md
git commit -m 'docs: update changelog'
git push origin main --follow-tags  # Triggers the publish
```

Confirm the version landed by checking the index, which is not cached the way the JSON endpoint is:

```sh
curl -s -H 'Accept: application/vnd.pypi.simple.v1+json' https://pypi.org/simple/corallium/ | jq -r '.versions[-1]'
```

### Known follow-ups

The changelog steps above are manual only because this project pins `calcipy>=6.0.1`. calcipy 6.1.0rc0 regenerates the changelog as part of `./run release`, writing it straight to `docs/docs/CHANGELOG.md` after the tag exists so the entry carries the new version instead of filing it under `Unreleased`. uv skips prereleases by default, so picking that up means allowing the prerelease or waiting for 6.1.0 final. Once it lands, drop the `commitizen changelog` and `mv` lines and keep the commit.

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
| `corallium/loggers/rich_printer.py`                       | 44         | 7       | 0        | 80.0%    |
| `corallium/loggers/structlog_logger/__init__.py`          | 3          | 0       | 3        | 100.0%   |
| `corallium/loggers/structlog_logger/_structlog_logger.py` | 8          | 0       | 0        | 100.0%   |
| `corallium/loggers/styles.py`                             | 38         | 3       | 0        | 88.1%    |
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
| **Totals**                                                | 1043       | 126     | 55       | 85.0%    |

Generated on: 2026-08-31
<!-- {cte} -->
