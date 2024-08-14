# Changelog

All notable changes to this project will be documented in this file.

## 2.6.3 (2024-08-14)

- Updated pydantic to the latest 1.x version to address incompatibility with python 3.12.4. Ref: https://github.com/pydantic/pydantic/issues/9637

## 2.6.2 (2024-04-25)

- Added support for Python 3.11 and 3.12.
- Updated Dockerfile to use Python 3.12.
- Added docker-build.yml action.

## 2.6.1 (2024-04-25)

- Updated all dependencies.
- Fixed a bug with usage frequency parsing (#48).

## 2.6.0 (2023-04-23)

- Added SQLite cache and made it the default one.
- Made MemoryCache use LRU.
- Added tests for all cache classes.
- Updated Dockerfile to use /cache for file and SQLite caches.
- Added a sample docker-compose file.
- Updated FastAPI and httpx dependencies.

## 2.5.1 (2022-11-19)

- Added FAQ to the README, where provided a clearer explanation of the 503 error.

## 2.5.0 (2022-11-19)

- Added "follow_corrections" API flag (#23)
- Added configuration to host the project on fly.io
- Updated the address of the sample installation to https://linguee-api.fly.dev
- Added lemma forms (#26)

## 2.4.0 (2022-08-01)

- Set Heroku runtime to python-3.10.5 (#21)
- Added "usage_frequency" attribute to translations (#22)

## 2.3.0 (2022-06-17)

- Added packaging support
- Added support for various versions of Python (3.8+)
- Updated httpx to the latest version. Ref: CVE-2021-41945

## 2.2.1 (2022-04-20)

- Updated development dependencies and pre-commit hooks
- Provided usage examples for Python and Bash

## 2.2.0 (2021-09-28)

- Fixed a bug with multiple grammar infos (#12).
- Fixed a file cache issue on the Windows platform (#16).
- Updated all dependencies to their latest versions.

## 2.1.0 (2021-05-16)

- Added translation examples to the /translations API endpoint (#10).

## 2.0.0 (2021-04-29)

- The first release of the Python version of the project.
