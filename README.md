# Users Package
[![Release](https://github.com/obervinov/users-package/actions/workflows/release.yaml/badge.svg)](https://github.com/obervinov/users-package/actions/workflows/release.yaml)
[![CodeQL](https://github.com/obervinov/users-package/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/obervinov/users-package/actions/workflows/github-code-scanning/codeql)
[![Tests and Checks](https://github.com/obervinov/users-package/actions/workflows/pr.yaml/badge.svg)](https://github.com/obervinov/users-package/actions/workflows/pr.yaml)

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/obervinov/users-package?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/obervinov/users-package?style=for-the-badge)
![GitHub Release Date](https://img.shields.io/github/release-date/obervinov/users-package?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/obervinov/users-package?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/obervinov/users-package?style=for-the-badge)

## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/book.png" width="25" title="about"> About this project
**Project Description**

This Python module is designed to simplify user management in __Telegram Bots__ by providing necessary functionality such as: `authentication`, `authorization` and `request limitation`, providing efficient management of user attributes and access rights.

Interaction Model 1: Using a Unified Entrypoint (Method: `user_access_check()`)
```mermaid
sequenceDiagram
    participant Bot
    participant Users-Module
    Bot->>Users-Module: Create Users-Module instance with rate limits
    Bot->>Users-Module: Call user_access_check(user_id, role_id)
    Users-Module-->>Bot: Return access, permissions, and rate limits
```

**Key Features**

- This module is designed primarily for Telegram bots but can be adapted for various projects that require user management, role-based access control, and request rate limiting.

- This module requires certain dependencies related to
    - [Vault](https://www.vaultproject.io)
      - [Vault Server](docker-compose.ymla) for storing user configurations and historical data
      - [Additional Module](https://github.com/obervinov/vault-package ) to interact with the Vault API
      - [Vault Policy](tests/vault/policy.hcl) with access rights to the Vault Server
    - [PostgreSQL](https://www.postgresql.org)
      - [PostgreSQL Server](docker-compose.yml) for storing user data and historical records
      - [PostgreSQL Schema](tests/postgres/tables.sql) for creating tables in the database

**Table of Contents**
- [Description of module Constants](#-description-of-module-constants)
- [Description of module Exceptions](#-description-of-module-exceptions)
- [Users class](#-users-class)
- [RateLimiter class](#-ratelimiter-class)
- [Storage class](#-storage-class)
- [Structure of configuration in Vault](#-structure-of-configuration-in-vault)
- [Structure of historical data in PostgreSQL](#-structure-of-historical-data-in-postgresql)
- [Additional usage example](#-additional-usage-example)
- [Installing](#-installing)


## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/stack2.png" width="21" title="constants"> Description of module Constants

This module contains constant values

| Constant Name             | Description                                       | Default Value           |
|---------------------------|---------------------------------------------------|-------------------------|
| `USERS_VAULT_CONFIG_PATH` | Path for configuration data in Vault.             | `"configuration/users"` |
| `USER_STATUS_ALLOW`       | User access status for allowed access.            | `"allowed"`             |
| `USER_STATUS_DENY`        | User access status for denied access.             | `"denied"`              |


## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/stack2.png" width="21" title="exceptions"> Description of module Exceptions
| Exception                    | Describe                              | Tips |
|------------------------------|---------------------------------------|------|
| `WrongUserConfiguration`     | Raised when user configuration is wrong. | Please, see the configuration [example](#-structure-of-configuration-and-statistics-data-in-vault) |
| `VaultInstanceNotSet`        | Raised when the Vault instance is not set. | Please, see [documentation](#class-initialization) |
| `FailedDeterminateRateLimit` | Raised when the rate limit cannot be determined. | Please, check misconfiguration between configuration and users requests in PostgreSQL |
| `StorageInstanceNotSet`      | Raised when the storage instance (PostgreSQL) is not set. | Please, see [documentation](#class-initialization) |
| `FailedStorageConnection`    | Raised when the connection to the storage (PostgreSQL) failed. | Please, check the connection to the PostgreSQL server |


## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/build.png" width="25" title="class"> Users class
### Class Initialization

The `Users` class provides authentication, authorization, user attribute management and user request logging for Telegram bots. You can initialize it with different options

- `vault (any)`: Configuration for initializing the Vault client.
  - `(object)`: an already initialized instance of VaultClient for interacting with the Vault API.
  - `(dict)`: extended configuration for VaultClient (for database engine).
    - `instance (VaultClient)`: An already initialized instance for interacting with the Vault API.
    - `role (str)`: The role name for the Vault database engine.

- `rate_limits (bool)`: Enable rate limit functionality.

- `storage_connection (any)`: Connection object to connect to the storage. Do not use if you are using Vault database engine.
- **Examples:**

  - Initialize with `VaultClient` and without `rate_limits`:
    ```python
    users_without_ratelimits = Users(vault=<VaultClient>, rate_limits=False, storage_connection=psycopg2.connect(**db_config))
    ```

  - Initialize with `VaultClient` and with `rate_limits`:
    ```python
    users_with_ratelimits = Users(vault=<VaultClient>, storage_connection=psycopg2.connect(**db_config))
    ```

  - Initialize with Vault `configuration dictionary` (for using the vault database engine):
    ```python
    vault_config = {'instance': <VaultClient>, 'role': 'my_db_role'}
    users_with_dict_vault = Users(vault=vault_config)
    ```

### decorator: Access Control

The `access_control()` decorator is used to control access to specific functions based on user roles and permissions.</br>
**Required the `pyTelegramBotAPI` objects:** `telegram.telegram_types.Message` or `telegram.telegram_types.CallbackQuery`

- **Arguments:**
  - `role_id (str)`: Required role ID for the specified user ID.
  - `flow (str)`: The flow of the function, which can be either.
    - `auth` for authentication. Default value.
    - `authz` for authorization.

- **Examples:**</br>
  Role-based access control
  ```python
    @telegram.message_handler(commands=['start'])
    @access_control(role_id='admin_role', flow='authz')
    # Decorator returns user information about access, permissions, and rate limits into access_result argument
    def my_function(message: telegram.telegram_types.Message, access_result: dict = None):
        print(f"User permissions: {access_result}")
        pass
  ```
  Just authentication
  ```python
    @telegram.message_handler(commands=['start'])
    @access_control()
    # Decorator returns user information about access, permissions, and rate limits into access_result argument
    def my_function(message: telegram.telegram_types.Message, access_result: dict = None):
        print(f"User permissions: {access_result}")
        pass
  ```

- **Returns:**
  - Breaks the function and returns an error message if the user does not have the required role or permission.

### method: User Access Check

The `user_access_check()` method is the main entry point for authentication, authorization, and request rate limit verification. It is used to control the request rate (limits) for a specific user.

- **Arguments:**
  - `user_id (str)`: Required user ID.
  - `role_id (str)`: Required role ID for the specified user ID.

- **Keyword Arguments:**
  - `chat_id (str)`: Required chat ID for the specified user ID. Additional context for logging.
  - `message_id (str)`: Required message ID for the specified user ID. Additional context for logging.

- **Examples:**
  ```python
  user_access_check(user_id='user1', role_id='admin_role', chat_id='chat1', message_id='msg1')
  ```

- **Returns:**
  - A dictionary with access status, permissions, and rate limit information.
    ```python
    {
      'access': self.user_status_allow / self.user_status_deny,
      'permissions': self.user_status_allow / self.user_status_deny,
      'rate_limits': '2023-08-06 11:47:09.440933' / None
    }
    ```

### Description of class attributes
| Data Type | Attribute           | Purpose                                                      | Default Value           |
|-----------|---------------------|--------------------------------------------------------------|-------------------------|
| `object`  | `vault`             | Vault instance for interacting with the Vault API.           | `None`                  |
| `dict`    | `storage`           | Configuration for initializing the storage client.           | `None`                  |
| `bool`    | `rate_limits`       | Enable request rate limit functionality.                     | `True`                  |
| `str`     | `user_status_allow` | User access status: allowed.                                 | `"allowed"`             |
| `str`     | `user_status_deny`  | User access status: denied.                                  | `"denied"`              |
| `str`     | `vault_config_path` | The prefix of the configuration path in the Vault.           | `"configuration/users"` |


## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/build.png" width="25" title="class"> RateLimiter class
### Class Initialization

The `RateLimiter` class provides restriction functionality for user requests to the Telegram bot in the context of a specific user.

- `vault (VaultClient)`: An already initialized instance for interacting with the Vault API or a configuration dictionary for initializing a VaultClient instance in this class.

- storage (Storage): An already initialized instance for interacting with the storage (PostgreSQL) or a configuration dictionary for initializing a Storage instance in this class.

- `user_id (str)`: User ID for checking speed limits.

- **Examples:**
  ```python
  limiter = RateLimiter(vault=<VaultClient>, storage=storage_client, user_id='User1')
  ```

### method: Rate Limit Determination

The `determine_rate_limit()` method is the main entry point for checking bot request limits for the specified user. It returns information about whether the request rate limits are active and when they expire 

- **Examples:**
  ```python
  determine_rate_limit()
  ```

- **Returns:**
  - String with a `timestamp` of the end of restrictions on requests or `None` if rate limit is not applied.
    ```python
    ("2023-08-07 10:39:00.000000" | None)
    ```

### method: Get User Requests Counters

The `get_user_request_counters()` method calculates the number of requests made by the user and returns the number of requests per day and per hour.

- **Examples:**
  ```python
  get_user_request_counters()
  ```

- **Returns:**
  - A dictionary with the number of requests per day and per hour.
    ```python
    {
      'requests_per_day': 9,
      'requests_per_hour': 1
    }
    ```

### Description of Class Attributes
| Data Type      | Attribute                | Purpose                                                                  | Default Value                   |
|----------------|--------------------------|--------------------------------------------------------------------------|---------------------------------|
| `VaultClient`  | `vault`                  | Vault instance for interacting with the Vault API.                       | `None`                          |
| `Storage`      | `storage`                | Storage instance for interacting with the storage (PostgreSQL).          | `None`                          |
| `str`          | `user_id`                | User ID for checking speed limits.                                       | `None`                          |
| `str`          | `vault_config_path`      | The prefix of the configuration path in the Vault.                       | `"configuration/users"`         |
| `dict`         | `requests_configuration` | User request limits configuration.                                       | `None`                          |
| `dict`         | `requests_counters`      | Counters for the number of requests per day and per hour.                | `None`                          |


## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/build.png" width="25" title="class"> Storage class
### Class Initialization
The storage class for the storage of user data: requests, access logs, etc in the PostgreSQL database.</br>
**Only one of the parameters is required for initialization: `db_connection` or `vault`**.

- `db_connection (object)`: The database connection object for interacting with the PostgreSQL database (psycopg2).

- `vault (dict)`: Configuration for initializing the Vault client.
  - `instance (VaultClient)`: An already initialized instance for interacting with the Vault API.
  - `role (str)`: The role name for the Vault database engine.

- **Examples:**
  ```python
  storage = Storage(db_connection=psycopg2.connect(**db_config))
  ```
  ```python
  storage = Storage(vault={'instance': <VaultClient>, 'role': 'my_db_role'})
  ```

### method: Create connection to the PostgreSQL database
The `create_connection()` method creates a connection to the PostgreSQL database.

- **Examples:**
```python
create_connection()
```

- **Returns:**
  - Connection object to the PostgreSQL database.

### method: Register of User
The `register_user()` method registers a new user in the database.

- **Arguments:**
  - `user_id (str)`: User ID for registration.
  - `chat_id (str)`: Chat ID for registration.
  - `status (str)`: The user state in the system. Values: `self.user_status_allow` or `self.user_status_deny`.

- **Examples:**
  ```python
  register_user(user_id='user1', chat_id='chat1', status='allowed')
  ```

### method: Log user request
The `log_user_request()` method logs the user request in the database.

- **Arguments:**
  - `user_id (str)`: User ID for logging.
  - `request (dict)`: The user request details.

- **Examples:**
  ```python
  log_user_request(user_id='user1', request={'chat_id': 'chat1', 'message_id': 'msg1'})
  ```

### method: Get user requests
The `get_user_requests()` method retrieves the user's requests from the database.

- **Arguments:**
  - `user_id (str)`: User ID for retrieving requests.
  - `limit (int)`: The number of requests to retrieve.
  - `order (str)`: The order of the requests. Values: `asc` or `desc`.

- **Examples:**
  ```python
  get_user_requests(user_id='user1', limit=10, order='asc')
  ```

- **Returns:**
  - A list of user requests `[(id, timestamp, rate_limits), ...]`.

### method: Get users
The `get_users()` method retrieves all users from the database.

- **Arguments:**
  - `only_allowed (bool)`: Retrieve only allowed users.

- **Examples:**
  ```python
  get_users()
  ```

- **Returns:**
  - A list of users `[{'user_id': '12345', 'chat_id': '67890', 'status': 'denied'}, ...]`.


## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/requirements.png" width="25" title="configuration-structure"> Structure of configuration in Vault
This project uses a Vault server with the KV2 engine and Database Engine for storing user configurations and database connection data.
It supports user configurations to define system access rights, roles, and request restrictions.

### Users Configuration
- **path to the secret**: `configuration/users/{user_id}`
- **keys and Values**:
  - `status`: The status of user access, which can be either
      - `self.user_status_allow`
      - `self.user_status_deny`
  - `roles`: A list of roles associated with the user ID, e.g., `["role1", "role2"]`.
  - `requests`: Limits on the number of requests
      - `requests_per_day`
      - `requests_per_hour`
      - `random_shift_time` (additional, random shift in minutes from 0 to the specified number) in minutes

- **example of a secret with configuration**:
```json
{
  "status": "allowed",
  "roles": ["admin_role", "additional_role"],
  "requests": {
    "requests_per_day": 10,
    "requests_per_hour": 1,
    "random_shift_minutes": 15
  }
}
```

### Database Configuration
- **path to the secret**: `configuration/database`

- **keys and values with simple database connection**:
  - `host`: The host of the PostgreSQL server.
  - `port`: The port of the PostgreSQL server.
  - `database`: The name of the PostgreSQL database.
  - `user`: The username for the PostgreSQL database.
  - `password`: The password for the PostgreSQL database.

  ```json
  {
    "host": "localhost",
    "port": 5432,
    "dbname": "mydatabase",
    "user": "myuser",
    "password": "mypassword",
  }
  ```

- **keys and values with Vault Database Engine**:
  - `role`: The role name for the Vault database engine.
  - `instance`: The instance of the VaultClient for interacting with the Vault API.

  ```json
  {
    "host": "localhost",
    "port": 5432,
    "dbname": "mydatabase",
  }
  ```

## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/requirements.png" width="25" title="data-structure"> Structure of historical data in PostgreSQL
This project uses a PostgreSQL database to store historical data about user requests and access events. It supports user request logging to track user activity and access rights.
The detailed table schema can be found in this [sql file](tests/postgres/tables.sql).

### Users Requests Table
Contains records of user requests, access permission, access level, and apply limits on the number of requests.

### Users Table
Contains records of user metadata for the Telegram bot, such as user ID, chat ID, and message ID.

## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/config.png" width="25" title="usage"> Additional usage example
Example 1 - With Rate Limits
```python
# import modules
from vault import VaultClient
from users import Users

# create the vault client
vault_client = VaultClient(
  url='http://0.0.0.0:8200',
  namespace='my_project',
  auth={
      'type': 'approle',
      'role_id': 'my_role',
      'secret_id': 'my_secret_id'
  }
)

# create the Users instance of the class with rate limits and get user information
users = Users(vault=<VaultClient>, rate_limits=True, storage_connection=psycopg2.connect(**db_config))
user_info = users.user_access_check(user_id=message.chat.id, role_id="admin_role", chat_id=message.chat.id, message_id=message.message_id)

# check permissions, roles, and rate limits
if user_info["access"] == users.user_status_allow:
    print("Hi, you can use the bot!")
    if user_info["permissions"] == users.user_status_allow:
        if user_info["rate_limits"]:
            print(f"You have sent too many requests, the limit is applied until {user_info['rate_limits']}")
        else:
            print("You have admin's rights")
    else:
        print("You do not have access rights to this function")
else:
    print("Access denied, goodbye!")
```

Example 2 - Without Rate Limits
```python
# import modules
from vault import VaultClient
from users import Users

# create the vault client
vault_client = VaultClient(
  url='http://vault.example.com',
  namespace='my_project',
  auth={
      'type': 'approle',
      'role_id': 'my_role',
      'secret_id': 'my_secret_id'
  }
)

# create the Users instance of the class without rate limits and get user information
users = Users(vault=<VaultClient>, storage_connection=psycopg2.connect(**db_config))
user_info = users.user_access_check(user_id=message.chat.id, role_id="admin_role", chat_id=message.chat.id, message_id=message.message_id)

# check permissions and roles
if user_info["access"] == users.user_status_allow:
    print("Hi, you can use the bot!")
    if user_info["permissions"] == users.user_status_allow:
        print("You have admin's rights")
    else:
        print("You do not have access rights to this function")
else:
    print("Access denied, goodbye!")
```

Example 3 - Decorator Usage
```python
# import modules
from vault import VaultClient
from users import Users

# create the vault client
vault_client = VaultClient(
  url='http://vault.example.com',
  namespace='my_project',
  auth={
      'type': 'approle',
      'role_id': 'my_role',
      'secret_id':
  }
)

# create the Users instance of the class with rate limits
users = Users(vault=<VaultClient>, rate_limits=True, storage_connection=psycopg2.connect(**db_config))

# create a function with the access_control decorator
@telegram.message_handler(commands=['start'])
@access_control()
# Decorator returns user information about access, permissions, and rate limits into access_result argument
def my_function(message: telegram.telegram_types.Message, access_result: dict = None):
    print(f"User permissions: {access_result}")
    pass

# call the function
my_function(message)
```


## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/stack2.png" width="20" title="install"> Installing
```bash
tee -a pyproject.toml <<EOF
[tool.poetry]
name = myproject"
version = "1.0.0"
description = ""

[tool.poetry.dependencies]
python = "^3.12"
users = { git = "https://github.com/obervinov/users-package.git", tag = "v4.1.0" }

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

poetry install
```

## <img src="https://github.com/obervinov/_templates/blob/v1.0.5/icons/github-actions.png" width="25" title="github-actions"> GitHub Actions
| Name  | Version |
| ------------------------ | ----------- |
| GitHub Actions Templates | [v2.1.1](https://github.com/obervinov/_templates/tree/v2.1.1) |