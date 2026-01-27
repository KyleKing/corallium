# Corallium PR Review - Actionable Tasks

## Changes in This PR

### New Modules (from calcipy)

| Module | Purpose | Tests Needed |
|--------|---------|--------------|
| `can_skip.py` | Make-style build skip logic | Yes |
| `code_tag_collector/` | TODO/FIXME collection with git blame | Yes |
| `file_search.py` | Git-based file discovery | Yes |
| `markdown_table.py` | Markdown table formatting | Yes |
| `sync_dependencies.py` | Lock file version syncing | Yes |

### Fixes Applied

- `shell.py`: Added `validate_cmd` parameter with `_validate_shell_command()`
- `file_helpers.py`: Chunked `tail_lines()` for performance
- `file_helpers.py`: Added `RESERVED_NAMES` for Windows compatibility
- `file_helpers.py`: Fixed `_parse_tool_versions()` to handle tabs/multiple spaces
- `pretty_process.py`: Added `sleep(0.1)` to avoid busy-waiting
- `pretty_process.py`: Simplified chunking with `math.ceil()`

---

## Remaining Tasks

### Code Quality

1. **code_tag_collector/_collector.py**
   - Remove redundant `beartype.typing` imports (shadows stdlib `Pattern`)
   - Change `_CollectorRow` to `@dataclass(frozen=True)` for consistency
   - Update default header from "calcipy" to "corallium"

2. **file_helpers.py**
   - `delete_old_files()`: Skip symlinks to prevent unexpected deletions
   - `trim_trailing_whitespace()`: Handle CRLF line endings

3. **Public API**
   - Decide which new modules should be exported in `__init__.py`
   - Currently only `format_table` is exported

### Tests Required

All new modules lack test coverage:
- `tests/test_can_skip.py`
- `tests/test_code_tag_collector.py`
- `tests/test_file_search.py`
- `tests/test_markdown_table.py`
- `tests/test_sync_dependencies.py`

---

## Cross-Package Changes

### calcipy

After corallium changes are released, calcipy should:

1. **Remove migrated modules:**
   - `calcipy/can_skip.py` → use `corallium.can_skip`
   - `calcipy/code_tag_collector/` → use `corallium.code_tag_collector`
   - `calcipy/file_search.py` → use `corallium.file_search`
   - `calcipy/markdown_table.py` → use `corallium.markdown_table`
   - `calcipy/sync_dependencies.py` → use `corallium.sync_dependencies`

2. **Update imports:**
   ```python
   # Before
   from calcipy.can_skip import can_skip
   # After
   from corallium.can_skip import can_skip
   ```

3. **Add corallium dependency with tags extra:**
   ```toml
   corallium = { version = ">=2.2.0", extras = ["tags"] }
   ```

### tail-jsonl

1. **Remove `styles_from_dict()` wrapper** in `config.py`
   - Use `Styles.from_dict()` from corallium directly

2. **Keep dotted key promotion logic** in `core.py`
   - Too application-specific for corallium

---

## Decisions Made

### file_search.py Placement

**Decision:** Keep `file_search.py` in corallium.

**Rationale:**
- `code_tag_collector` depends on it
- Lightweight module (~130 lines) with no external dependencies
- Only uses `capture_shell()` from corallium itself

**Note:** Git must be available when using `file_search` or `code_tag_collector` modules.
