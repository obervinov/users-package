"""This module contains the storage class for the storage of user data: requests, access logs, etc."""
import psycopg2
from .exceptions import FailedStorageConnection


class Storage:
    """The storage class for the storage of user data: requests, access logs, etc."""
    def __init__(
        self,
        vault_client: object = None,
        db_role: str = None
    ) -> None:
        """
        Initialize the storage class with the database connection and credentials.

        Args:
            vault_client (object): The Vault client object.
            db_role (str): The database role for generating credentials from Vault.

        Returns:
            None

        Raises:
            FailedStorageConnection: An error occurred when the storage connection fails.

        Example:
            >>> storage = Storage(database_connection, database_credentials)
        """
        # Extract the database connection and credentials from Vault
        database_connection = vault_client.kv2engine.read_secret(path="configuration/database")
        database_credentials = vault_client.dbengine.generate_credentials(role=db_role)

        if not database_connection['dbname'] or not database_connection['host'] or not database_connection['port']:
            raise FailedStorageConnection("Invalid database connection configuration. Check keys 'dbname', 'host' and 'port'")
        if not database_credentials['user'] or not database_credentials['password']:
            raise FailedStorageConnection("Invalid database credentials configuration. Check keys 'user' and 'password'")

        self.connection = psycopg2.connect(
            host=database_connection['host'],
            port=database_connection['port'],
            user=database_credentials['user'],
            password=database_credentials['password'],
            dbname=database_connection['dbname']
        )
        self.cursor = self.connection.cursor()

    def write_access_log(
        self,
        user_id: str = None,
        details: dict = None,
        status: str = None
    ) -> None:
        """
        Write access logs to the database with the user access status.

        Args:
            user_id (str): The user ID.
            details (dict): The user access details.
            status (str): The user access status.

        Returns:
            None

        Example:
            >>> storage = Storage(database_connection, database_credentials)
            >>> storage.write_access_logs("user1", {"type": "authorization", "role": "admin"}, "allowed")
        """
        self.cursor.execute(f"INSERT INTO access_logs (user_id, details, status) VALUES ('{user_id}', '{details}', '{status}')")
        self.connection.commit()
