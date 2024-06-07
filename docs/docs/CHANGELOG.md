## Unreleased

## 2.0.0 (2024-06-07)

### Fix

- upgrade calcipy to latest and apply changes
- remove lower case log.logger; use log.LOGGER

## 1.0.3 (2024-06-07)

### Fix

- resolve pylint and ruff warnings
- copier-auto-update

## 1.0.2 (2024-05-29)

### Fix

- add missing typing-extensions

## 1.0.1 (2024-05-29)

### Fix

- remove depdency on pydantic

## 1.0.0 (2024-04-16)

### Fix

- delegated tasks must accept positional arguments
- drop Python 3.8

## 0.3.3 (2023-08-13)

### Fix

- correct copier update that broke Python <=3.10 support

## 0.3.2 (2023-08-13)

### Fix

- bump minimum pydantic to avoid beartype c-error
- remove beartype from lru_cache

## 0.3.1 (2023-08-12)

### Fix

- support beartype.claw type checking

## 0.3.0 (2023-06-21)

### Feat

- add capture shell async

### Perf

- use the logger global instead of the function

## 0.2.2 (2023-05-16)

### Fix

- bump minimum pymdown dependency

### Refactor

- run main task

## 0.2.1 (2023-04-22)

### Fix

- default to 'utf-8' when reading files

## 0.2.0 (2023-04-22)

### Feat

- add structlog and print loggers. Remove not implemented writer

## 0.1.1 (2023-04-07)

### Fix

- reduce rich exception length

## 0.1.0 (2023-02-25)

### Feat

- make Styles configurable

## 0.1.0rc3 (2023-02-24)

### Refactor

- extract the level lookups to replace singledispatch
- experiment with singledispatch and extending Styles for tail-jsonl

## 0.1.0rc2 (2023-02-23)

### Fix

- resolve issue with log setup

### Refactor

- move loggers into submodule for reuse and interchangeability
- merge logic from tail-jsonl
- experiment with different default log styles

## 0.1.0rc1 (2023-02-22)

### Fix

- raise the minimum calcipy version

## 0.1.0rc0 (2023-02-21)

### Feat

- absorb shoal and calcipy code
