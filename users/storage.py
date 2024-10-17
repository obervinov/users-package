"""This module contains the storage class for the storage of user data: requests, access logs, etc."""
import json
import psycopg2
from logger import log
from .exceptions import FailedStorageConnection


class Storage:
    """
    The storage class for the storage of user data: requests, access logs, etc.

    Attributes:
        connection (object): The database connection object.
        cursor (object): The database cursor object.

    Methods:
        register_user: Register the user in the
        log_user_request: Write the user requests to the database.
        get_user_requests: Get the user requests from the database.

    Raises:
        FailedStorageConnection: An error occurred when the storage connection fails.
    """
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

        Example:
            >>> storage = Storage(database_connection, database_credentials)
        """
        # Extract the database connection and credentials from Vault
        database_connection = vault_client.kv2engine.read_secret(path="configuration/database")
        database_credentials = vault_client.dbengine.generate_credentials(role=db_role)

        if database_connection and database_credentials:
            if not database_connection.get('dbname', None) or not database_connection.get('host', None) or not database_connection.get('port', None):
                raise FailedStorageConnection("Invalid database connection configuration. Check keys 'dbname', 'host' and 'port'")
            if not database_credentials.get('username', None) or not database_credentials.get('password', None):
                raise FailedStorageConnection("Invalid database credentials configuration. Check keys 'username' and 'password'")
        else:
            log.error('[Users]: Failed to initialize the storage class: database_connection %s, database_credentials %s', database_connection, database_credentials)
            raise FailedStorageConnection("Failed to get the database connection or credentials from Vault")

        self.connection = psycopg2.connect(
            host=database_connection['host'],
            port=database_connection['port'],
            user=database_credentials['username'],
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

        Example:
            >>> storage = Storage(database_connection, database_credentials)
            >>> storage.register_user("user1", "chat1", "allowed")
        """
        try:
            self.cursor.execute(f"INSERT INTO users (user_id, chat_id, status) VALUES ('{user_id}', '{chat_id}', '{status}')")
            self.connection.commit()
            log.info('[Users]: %s has been successfully registered in the database.', user_id)
        # pylint: disable=no-member
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            self.cursor.execute(f"UPDATE users SET chat_id='{chat_id}', status='{status}' WHERE user_id='{user_id}'")
            self.connection.commit()

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

        Example:
            >>> storage = Storage(database_connection, database_credentials)
            >>> storage.log_user_request("user1", {"type": "GET", "path": "/users"})
        """
        # Prepare values for the database
        request['authorization'] = json.dumps(request['authorization'])
        if request['rate_limits']:
            sql_query = (
                "INSERT INTO users_requests (user_id, message_id, chat_id, authentication, \"authorization\", rate_limits) VALUES ("
                f"'{user_id}', '{request['message_id']}', '{request['chat_id']}', '{request['authentication']}', "
                f"'{request['authorization']}', '{request['rate_limits']}')"
            )
        else:
            sql_query = (
                "INSERT INTO users_requests (user_id, message_id, chat_id, authentication, \"authorization\") VALUES "
                f"('{user_id}', '{request['message_id']}', '{request['chat_id']}', '{request['authentication']}', '{request['authorization']}')"
            )

        # Insert the user request into the database
        self.cursor.execute(sql_query)
        self.connection.commit()

    def get_user_requests(
        self,
        user_id: str = None,
        limit: int = 10000,
        order: str = "timestamp DESC"
    ) -> list:
        """
        Get the user requests from the database.

        Args:
            user_id (str): The user ID.
            limit (int): The number of requests to return.
            order (str): The order of the requests.

        Returns:
            list: The list of user requests.
            [(id, timestamp, rate_limits), ...]

        Example:
            >>> storage = Storage(database_connection, database_credentials)
            >>> storage.get_user_requests(user_id="user1", limit=10, order="timestamp DESC")
        """
        self.cursor.execute(f"SELECT id, timestamp, rate_limits FROM users_requests WHERE user_id='{user_id}' ORDER BY {order} LIMIT {limit}")
        return self.cursor.fetchall()

    def get_users(
        self,
        only_allowed: bool = True
    ) -> list:
        """
        Get a list of all users in the database.
        By default, the method returns only allowed users.

        Args:
            only_allowed (bool): A flag indicating whether to return only allowed users. Default is True.

        Returns:
            list: The list of users.
            [{'user_id': '12345', 'chat_id': '67890', 'status': 'denied'}, ...]

        Examples:
            >>> get_users()
            [{'user_id': '12345', 'chat_id': '67890', 'status': 'denied'}, {'user_id': '12346', 'chat_id': '67891', 'status': 'allowed'}]
        """
        users_list = []
        base_query = "SELECT user_id, chat_id, status FROM users"

        if only_allowed:
            condition = "WHERE status = 'allowed'"
        else:
            condition = ""

        self.cursor.execute(f"{base_query} {condition}")
        users = self.cursor.fetchall

        if users:
            for user in users:
                users_list.append({'user_id': user[0], 'chat_id': user[1], 'status': user[2]})
        return users_list
