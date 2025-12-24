# Change Log
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## v4.1.3 - 2025-12-24
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v4.1.2...v4.1.3 by @obervinov in https://github.com/obervinov/users-package/pull/77
#### 🚀 Features
* upgrade dependencies to latest versions


## v4.1.2 - 2025-07-15
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v4.1.1...v4.1.2 by @obervinov in https://github.com/obervinov/users-package/pull/63
#### 🚀 Features
* bump dependencies version


## v4.1.1 - 2025-03-26
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v4.1.0...v4.1.1 by @obervinov in https://github.com/obervinov/users-package/pull/55
#### 🐛 Bug Fixes
* add `rollback transaction` action in the `Storage` class exception handling block to prevent critical exceptions from breaking the database connection


## v4.1.0 - 2025-02-21
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v4.0.2...v4.1.0 by @obervinov in https://github.com/obervinov/users-package/pull/54
#### 🚀 Features
* bump dependencies version
* bump workflows version to `2.1.1`
* the functionality has been returned to establish its own connection to the database (in addition to the possibility of transferring an existing connection object) for more stable operation of the module with correct credentials via Vault DBEngine (for example, the bug https://github.com/obervinov/pyinstabot-downloader/issues/118)
#### 💥 Breaking Changes
* The `vault` input argument of the `Users()` class now expects an object or a new dict format `{'instance': <vault_object>, 'role': 'my-dbengine-role'}`. The previous vault dictionary format is no longer supported. 


## v4.0.2 - 2024-12-19
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v4.0.1...v4.0.2 by @obervinov in https://github.com/obervinov/users-package/pull/53
#### 🚀 Features
* [Feature request: Add a decorator for easier access verification](https://github.com/obervinov/users-package/issues/52)
* bump workflows version to `2.0.2`
#### 🐛 Bug Fixes
* [Bug: Denied users are not recorded in the database](https://github.com/obervinov/users-package/issues/51)


## v4.0.1 - 2024-10-22
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v4.0.0...v4.0.1 by @obervinov in https://github.com/obervinov/users-package/pull/50
#### 📚 Documentation
* actualized documentation in the `README.md` file

## v4.0.0 - 2024-10-22
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v3.0.2...v4.0.0 by @obervinov in https://github.com/obervinov/users-package/pull/49
#### 💥 Breaking Changes
* bump python version to `3.12`
* some arguments of the `Users` class and the `Storage` class have been replaced. Detailed information can be found in the [DEPRECATED.md](DEPRECATEDv3.md) file
#### 🚀 Features
* bump all dependencies to the latest versions
* bump workflows version to `2.0.0`
* [Feature request: Add support for a method that returns a dictionary of all users in the table](https://github.com/obervinov/users-package/issues/44)
* [Feature request: Storage should not retrieve the database connection data from the vault itself](https://github.com/obervinov/users-package/issues/47)
#### 🐛 Bug Fixes
* [Bug: The application tries to use credentials to access the database that have already expired](https://github.com/obervinov/users-package/issues/48)
* [Configuration `per_day` in RateLimit not working as expected](https://github.com/obervinov/users-package/issues/40)


## v3.0.2 - 2024-09-10
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v3.0.1...v3.0.2 by @obervinov in https://github.com/obervinov/users-package/pull/46
#### 🐛 Bug Fixes
* fixed hardcoded vault dbengine `mount_point` if vault argument is a dict


## v3.0.1 - 2024-09-10
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v3.0.0...v3.0.1 by @obervinov in https://github.com/obervinov/users-package/pull/45
#### 🐛 Bug Fixes
* replace wrong dependencies `psycopg2` -> `psycopg2-binary` in `pyproject.toml`


## v3.0.0 - 2024-08-22
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v2.0.5...v3.0.0 by @obervinov in https://github.com/obervinov/users-package/pull/43
#### 💥 Breaking Changes
* [Feature request: Add an additional backend - `Postgres` to store historical user data](https://github.com/obervinov/users-package/issues/41)
* Bump vault-package version to `3.0.0` (this version contains major changes)
* Detailed information about the deprecated methods, constants, arguments, properties, and return values can be found in the [DEPRECATED.md](DEPRECATEDv2.md) file
* Changed logger level to `INFO` for messages when the user `RateLimit` is exceeded
* Removed unused option to manually set `vault_client` attributes
#### 🚀 Features
* Bump workflows version to `1.2.8`
* Bump vault-package version to `3.0.0`
* Bump transitive dependencies
* [Feature request: Add an additional backend - `Postgres` to store historical user data](https://github.com/obervinov/users-package/issues/41)



## v2.0.5 - 2024-05-28
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v2.0.4...v2.0.5 by @obervinov in https://github.com/obervinov/users-package/pull/41
#### 📚 Documentation
* Update `*.md` templates
#### 🚀 Features
* Add `github-actions` in dependency bot
* Bump workflow version to `v1.2.2`
* Add new workflow jobs: `pr` and `milestone`
#### 🐛 Bug Fixes
* [Configuration `per_day` in RateLimit not working as expected](https://github.com/obervinov/users-package/issues/40)


## v2.0.4 - 2024-03-24
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v2.0.3...v2.0.4 by @obervinov in https://github.com/obervinov/users-package/pull/39
#### 🚀 Features
* add custom exceptions
#### 🐛 Bug Fixes
* [Incorrect record of authentication events and user authorization in Vault data](https://github.com/obervinov/users-package/issues/37)
* [Error when call `rl_controller.determine_rate_limit()`](https://github.com/obervinov/users-package/issues/38)
* Fixes various RateLimit class bugs related to request accounting and operation of request counters
* A little tests refactoring


## v2.0.3 - 2024-02-05
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v2.0.2...v2.0.3 by @obervinov in https://github.com/obervinov/users-package/pull/36
#### 🐛 Bug Fixes
* Fix support python 3.9 in the package and workflows


## v2.0.2 - 2024-01-29
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v2.0.1...v2.0.2 by @obervinov in https://github.com/obervinov/users-package/pull/35
#### 📚 Documentation
* [Fix extensions in workflows](https://github.com/obervinov/users-package/pull/35)
#### 🐛 Bug Fixes
* [Fix extensions in workflows](https://github.com/obervinov/users-package/pull/35)


## v2.0.1 - 2024-01-29
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v2.0.0...v2.0.1 by @obervinov in https://github.com/obervinov/users-package/pull/31
#### 📚 Documentation
* [Fix wrong links format by release/v2.0.0 in CHANGELOG.md](https://github.com/obervinov/users-package/issues/28)
#### 🐛 Bug Fixes
* [Fix bug with import constants](https://github.com/obervinov/users-package/issues/30)
* [Incorrect calculation of rate_limit if it is already applied and you need to calculate the timer for additional messages](https://github.com/obervinov/users-package/issues/32)
#### 🚀 Features
* [Migration from pip to poetry](https://github.com/obervinov/users-package/issues/34)
* [Dependency graph does not work correctly, sort it out and fix it network/dependencies](https://github.com/obervinov/users-package/issues/33)


## v2.0.0 - 2023-11-07
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v1.0.5...v2.0.0 by @obervinov in https://github.com/obervinov/users-package/pull/24
#### 📚 Documentation
* [Users:v2 expand access rights and user attributes](https://github.com/obervinov/users-package/issues/21)
* [Improvements to the Vault dependency](https://github.com/obervinov/users-package/issues/27)
#### 💥 Breaking Changes
* [Users:v2 expand access rights and user attributes](https://github.com/obervinov/users-package/issues/21)
* [Deprecate outdated class and methods users:v1](https://github.com/obervinov/users-package/issues/26)
#### 🚀 Features
* [Update template workflow to v1.0.5](https://github.com/obervinov/users-package/issues/23)
* [Users:v2 expand access rights and user attributes](https://github.com/obervinov/users-package/issues/21)
* [Improvements to the Vault dependency](https://github.com/obervinov/users-package/issues/27)


## v1.0.5 - 2023-06-21
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v1.0.4...v1.0.5 by @obervinov in https://github.com/obervinov/users-package/pull/20
#### 🐛 Bug Fixes
* [Fix badge with tests in README.md](https://github.com/obervinov/users-package/issues/17)
* [Fix the error that caused the workflow create_release to run twice - at pr/main](https://github.com/obervinov/users-package/issues/18)
#### 🚀 Features
* [Bump vault-package to v2.0.1](https://github.com/obervinov/users-package/issues/19)


## v1.0.4 - 2023-06-18
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v1.0.3...v1.0.4 by @obervinov in https://github.com/obervinov/users-package/pull/15
#### 🐛 Bug Fixes
* [Fix work with transit dependencies in setup.py](https://github.com/obervinov/users-package/issues/14)
#### 📚 Documentation
* [Add a description to the links in CHANGELOG.md](https://github.com/obervinov/users-package/issues/16)


## v1.0.3 - 2023-05-31
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v1.0.2...v1.0.3 by @obervinov in https://github.com/obervinov/users-package/pull/9
#### 🐛 Bug Fixes
* [Delete a block in tests if "name" == "main"](https://github.com/obervinov/users-package/issues/12)
* [Check how the module behaves if the user_id is not recorded in the vault](https://github.com/obervinov/users-package/issues/11)
* [Add dependencies between tasks in the GitHub Actions](https://github.com/obervinov/users-package/issues/13)
#### 🚀 Features
* [Add support for the new version of the vault-package:v2.0.0](https://github.com/obervinov/users-package/issues/10)
* [Replace the mock with a vault container for pytests](https://github.com/obervinov/users-package/issues/8)
* [GitHub Actions workflow updates: 2023.05.22](https://github.com/obervinov/users-package/issues/6)
#### 📚 Documentation
* [Documentation updates: pr template](https://github.com/obervinov/users-package/issues/7)


## v1.0.2 - 2023-03-28
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v1.0.1...v1.0.2 by @obervinov in https://github.com/obervinov/users-package/pull/2
#### 🐛 Bug Fixes
* renamed the directory with the code to the name of the module - `users`
* fixed errors in the doc string and the general code format
* log string formation rewritten from `f-string` to `%s lezzy` format
#### 📚 Documentation
* updated and expanded the documentation in the file [README.md](https://github.com/obervinov/users-package/blob/v1.0.2/README.md)
#### 💥 Breaking Changes
* [changed the structure](https://github.com/obervinov/users-package/tree/v1.0.2#-data-structure-in-vault) of saving **login events** and the structure of storing **access rights** for **user ids**
* removed `bot_name` argument in `UsersAuth.__init__`
* renamed method `check_permission()` -> `check_permissions()`
* renamed argument `chat_id` -> `user_id` in method `check_permissions()`
* changed the return result `success`/`failed` -> `allow`/`deny`
* the functionality of recording events in Vault has been moved to a separate method - [`record_event()`](https://github.com/obervinov/users-package/blob/v1.0.2/users/users.py#L74)
#### 🚀 Features
* updated [GitHub Actions](https://github.com/obervinov/_templates/tree/v1.0.2) version to `v1.0.2`
* updated [logger-package](https://github.com/obervinov/logger-package/tree/v1.0.1) version to `v1.0.1`
* added [tests](https://github.com/obervinov/users-package/tree/v1.0.2/tests)


## v1.0.1 - 2023-02-28
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v1.0.0...v1.0.1 by @obervinov in https://github.com/obervinov/users-package/pull/1
#### 🐛 Bug Fixes
* updated the code in accordance with the recommendations of **flake8** and **pylint**
* adjusted [pyproject.toml](https://github.com/obervinov/users-package/blob/v1.0.1/pyproject.toml) and [setup.py](https://github.com/obervinov/users-package/blob/v1.0.1/setup.py) for package delivery
#### 📚 Documentation
* updated and expanded the documentation in the file [README.md](https://github.com/obervinov/users-package/blob/v1.0.1/README.md)
#### 💥 Breaking Changes
* global **code recycling**: _removed old artifacts_ and _more comments added to the code_
#### 🚀 Features
* added github actions: **flake8**, **pylint** and **create release**
* added [SECURITY](https://github.com/obervinov/users-package/blob/v1.0.1/SECURITY.md)
* added [ISSUE_TEMPLATE](https://github.com/obervinov/users-package/tree/v1.0.1/.github/ISSUE_TEMPLATE)
* added [PULL_REQUEST_TEMPLATE](https://github.com/obervinov/users-package/tree/v1.0.1/.github/PULL_REQUEST_TEMPLATE)
* added [CODEOWNERS](https://github.com/obervinov/users-package/tree/v1.0.1/.github/CODEOWNERS)
* added [dependabot.yml](https://github.com/obervinov/users-package/tree/v1.0.1/.github/dependabot.yml)


## v1.0.0 - 2022-11-05
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/commits/v1.0.0
#### 💥 Breaking Changes
* **Module release**
