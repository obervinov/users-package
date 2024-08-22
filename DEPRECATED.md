# Deprecated Methods

This document provides information about deprecated methods in the project.

## Deprecated Methods

| Method | Reason for Deprecation | Date of Deprecation | Alternative |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- |
| `Users.authorization()` | This method has gone private and is no longer available for public use. | 2024-08-23 | Please use general entry point `Users.user_access_check()` instead. |
| `Users.authorization()` | This method has gone private and is no longer available for public use. | 2024-08-23 | Please use general entry point `Users.user_access_check()` instead. |

## Deprecated Constants
| Constant | Reason for Deprecation | Date of Deprecation | Alternative |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- |
| `Users.VAULT_CONFIG_PATH` | This constant has gone renamed. | 2024-08-23 | Please use `Users.USERS_VAULT_CONFIG_PATH` instead. |
| `Users.VAULT_DATA_PATH`   | This constant has gone removed. Because it is no longer needed. | 2024-08-23 | Please use `Users.USERS_VAULT_DATA_PATH` instead. |

## Deprecated Return Values
| Method | Reason for Deprecation | Date of Deprecation | Old Return Value | New Return Value |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- | -------------------------------------- |
| `Users.user_access_check()` | There is no need to return the timestamp in the dictionary, the string is sufficient. | 2024-08-23 | `{'access': 'allowed', 'permission': 'allowed', 'rate_limits': {'end_time': '2024-08-23T12:00:00Z'}}` | `{'access': 'allowed', 'permission': 'allowed', 'rate_limits': '2024-08-23T12:00:00Z'}` |
| `RateLimiter.determine_rate_limit()` | There is no need to return the timestamp in the dictionary, the datetime is sufficient. | 2024-08-23 | `{'end_time': '2024-08-23T12:00:00Z'}` | `datetime.datetime(2024, 8, 23, 12, 0, 0, tzinfo=datetime.timezone.utc)` |

## Deprecated Arguments
| Method | Reason for Deprecation | Date of Deprecation | Old Argument | New Argument |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- | -------------------------------------- |
| `RateLimiter()` | The `Users` class now expects a different type of `vault` argument | 2024-08-23 | `vault: dict` or `vault: object` | `vault: VaultClient` |
| `Users() ` | The `Users` class now has a different value for the argument `rate_limits` | 2024-08-23 | `True` | `False` |

## Deprecated Properties
| Property | Reason for Deprecation | Date of Deprecation | Alternative |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- |
| `RateLimiter.vault` | The `vault` property has been deleted for lack of use | 2024-08-23 | N/A |
| `RateLimiter.vault_data_path` | The `vault_data_path` property has been deleted for lack of use | 2024-08-23 | N/A |
| 'Users.vault` | The `vault` property has been deleted for lack of use | 2024-08-23 | N/A |
| `Users.vault_data_path` | The `vault_data_path` property has been deleted for lack of use | 2024-08-23 | N/A |

