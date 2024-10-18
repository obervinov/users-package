
## Deprecated Arguments
| Method | Reason for Deprecation | Date of Deprecation | Old Argument | New Argument |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- | -------------------------------------- |
| `Users()` | The `Users` class now expects new argument instead of `storage` dictionary | 2024-10-18 | `storage: dict` | `storage_connection` is psycopg2 connection object |
| `Storage()` | The `Storage` class now expects new argument instead of `db_role` and `vault_client` | 2024-10-18 | `db_role: str`, `vault_client: VaultClient` | `db_connection` is psycopg2 connection object |
