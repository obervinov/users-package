# Change Log
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).


## v2.0.1 - 2023-11-17
### What's Changed
**Full Changelog**: https://github.com/obervinov/users-package/compare/v2.0.0...v2.0.1 by @obervinov in https://github.com/obervinov/users-package/pull/31
#### 📚 Documentation
* [Fix wrong links format by release/v2.0.0 in CHANGELOG.md ](https://github.com/obervinov/users-package/issues/28)
#### 🐛 Bug Fixes
* [Fix bug with import constants](https://github.com/obervinov/users-package/issues/30)
* [Incorrect calculation of rate_limit if it is already applied and you need to calculate the timer for additional messages](https://github.com/obervinov/users-package/issues/32)


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
