# Users Package
[![Release](https://github.com/obervinov/users-package/actions/workflows/release.yml/badge.svg)](https://github.com/obervinov/users-package/actions/workflows/release.yml)
[![CodeQL](https://github.com/obervinov/users-package/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/obervinov/users-package/actions/workflows/github-code-scanning/codeql)
[![Tests and checks](https://github.com/obervinov/users-package/actions/workflows/tests.yml/badge.svg?branch=main&event=pull_request)](https://github.com/obervinov/users-package/actions/workflows/tests.yml)

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/obervinov/users-package?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/obervinov/users-package?style=for-the-badge)
![GitHub Release Date](https://img.shields.io/github/release-date/obervinov/users-package?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/obervinov/users-package?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/obervinov/users-package?style=for-the-badge)

## <img src="https://github.com/obervinov/_templates/blob/main/icons/book.png" width="25" title="about"> About this project
This module contains classes and functions for implementing the simplest authorization for telegram bots.

## <img src="https://github.com/obervinov/_templates/blob/main/icons/github-actions.png" width="25" title="github-actions"> GitHub Actions
| Name  | Version |
| ------------------------ | ----------- |
| GitHub Actions Templates | [v1.0.0](https://github.com/obervinov/_templates/tree/v1.0.0) |


## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="functions"> Supported functions
- Authentication users
- Check permission users

## <img src="https://github.com/obervinov/_templates/blob/main/icons/stack2.png" width="20" title="install"> Installing
```bash
# Install current version
pip3 install git+https://github.com/obervinov/users-package.git#egg=users
# Install version by branch
pip3 install git+https://github.com/obervinov/users-package.git@main#egg=users
# Install version by tag
pip3 install git+https://github.com/obervinov/users-package.git@v1.0.0#egg=users
```

## <img src="https://github.com/obervinov/_templates/blob/main/icons/config.png" width="25" title="usage"> Usage example
```python
"""Import module"""
import os
from users import UsersAuth


"""Environment variables"""
bot_name = os.environ.get('BOT_NAME', 'my-bot')


"""Create an instance of the class"""
Users_auth = UsersAuth(Vault, bot_name)


"""Checking whether there is a user in the whitelist configuration
type: str
return value: "success" or "faild"
"""
access_status = Users_auth.check_permission(message.chat.id)


"""Usage example"""
if access_status == "success":
   print("Hi")
else:
    log.error(f"403: Forbidden for username: {message.from_user.username}")
```
