"""This module contains the storage class for the storage of user data: requests, access logs, etc."""
import psycopg2
from logger import log
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

    def register_user(
        self,
        user_id: str = None,
        chat_id: str = None,
        status: str = None
    ) -> None:
        """
        Register the user in the database.

        Args:
            user_id (str): The user ID.
            chat_id (str): The chat ID.
            status (str): The user state.

        Returns:
            None

        Example:
            >>> storage = Storage(database_connection, database_credentials)
            >>> storage.register_user("user1", "chat1", "allowed")
        """
        try:
            self.cursor.execute(f"INSERT INTO users (user_id, chat_id, status) VALUES ('{user_id}', '{chat_id}', '{status}')")
            self.connection.commit()
            log.info(f"[Users]: {user_id} has been successfully registered in the database.")
        except psycopg2.errors.UniqueViolation:
            log.info(f"[Users]: {user_id} already exists in the database. Updating the chat ID and status.")
            self.cursor.execute(f"UPDATE users SET chat_id='{chat_id}', status='{status}' WHERE user_id='{user_id}'")
            self.connection.rollback()

    def log_user_request(
        self,
        user_id: str = None,
        request: dict = None
    ) -> None:
        """
        Write the user requests to the database.

        Args:
            user_id (str): The user ID.
            request (dict): The user request details.

        Parameters:


        Returns:
            None

        Example:
            >>> storage = Storage(database_connection, database_credentials)
            >>> storage.log_user_request("user1", {"type": "GET", "path": "/users"})
        """
        self.cursor.execute(
            "INSERT INTO users_requests (user_id, message_id, chat_id, authentication, authorization, rate_limits) VALUES "
            f"('{user_id}', '{request['message_id']}', '{request['chat_id']}', '{request['authentication']}', '{request['authorization']}', '{request['rate_limits']}')"
        )
        self.connection.commit()
