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
This module contains classes and methods for implementing the simplest authorization for telegram bots.

The list of rights and their binding to the user id is stored in the **Vault**, so the **Vault** is required for the module to work.

## <img src="https://github.com/obervinov/_templates/blob/main/icons/github-actions.png" width="25" title="github-actions"> GitHub Actions
| Name  | Version |
| ------------------------ | ----------- |
| GitHub Actions Templates | [v1.0.2](https://github.com/obervinov/_templates/tree/v1.0.2) |


## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="functions"> Supported functions
- Check permissions for user id
- Recording events about logging into the vault

## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="functions"> Data structure in Vault
The structure that the module expects to see in the Vault to determine `user id rights`
```bash
# permissions data
 % vault kv get configuration/permissions
========= Secret Path =========
configuration/data/permissions

======= Metadata =======
Key                Value
---                -----
created_time       2023-03-26T08:00:00.000000000Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

====== Data ======
Key         Value
---         -----
123456      allow
123457      allow
123458      deny
```

The structure in which the module stores `login events`
```bash
# Login events keys
 % vault kv list events/login
Keys
----
123456
123457
123458

# Login events data
 % vault kv get events/login/123456
========= Secret Path =========
events/login/data/123456

======= Metadata =======
Key                Value
---                -----
created_time       2023-03-26T08:00:00.000000000Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

====== Data ======
Key                           Value
---                           -----
2023-03-26 08:00:00.000000    deny
2023-03-26 09:00:00.000000    allow
2023-03-26 10:00:00.000000    allow
```


The `policy` required by the module when interacting with **Vault**
```bash
path "${mount_point}/configuration/data/permissions" {
  capabilities = ["read", "list"]
}
path "${mount_point}/events/login/*" {
  capabilities = ["read", "list", "create", "update"]
}

```

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

"""Create an instance of the class"""
users_auth = UsersAuth(vault_client)

"""Checking whether there is a user in the whitelist configuration
type: str
return value: "allow" or "deny"
"""
if users_auth.check_permissions(message.chat.id) == "allow":
   print("Hi")
```
