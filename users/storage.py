"""This module contains the storage class for the storage of user data: requests, access logs, etc."""
import json
import time
import psycopg2
from logger import log
from .exceptions import FailedStorageConnection


def reconnect_on_exception(method):
    """
    A decorator that catches the closed cursor exception and reconnects to the database.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except psycopg2.Error as exception:
            log.warning('[Users]: Connection to the database was lost: %s. Attempting to reconnect...', str(exception))
            time.sleep(5)
            try:
                self.connection = self.create_connection()
                log.info('[Users]: Reconnection successful. Rolling back the transaction...')
                self.connection.rollback()
                return method(self, *args, **kwargs)
            except psycopg2.Error as inner_exception:
                log.error('[Users]: Failed to reconnect to the database: %s', str(inner_exception))
                raise inner_exception
    return wrapper


class Storage:
    """
    The storage class for the storage of user data: requests, access logs, etc.

    Attributes:
        db_connection (object): The database connection object from the psycopg2 library.
        vault (dict): Alternative way to provide the database connection settings.
            :param instance (object): The Vault object.
            :param role (str): The database role.
        connection (psycopg2.connect): The database connection object.
        cursor (psycopg2.cursor): The database cursor object.

    Methods:
        create_connection: Create a connection for the PostgreSQL
        register_user: Register the user in the
        log_user_request: Write the user requests to the database.
        get_user_requests: Get the user requests from the database.
        get_users: Get a list of all users in the database.

    Raises:
        FailedStorageConnection: An error occurred when the storage connection fails.
    """
    def __init__(self, db_connection: object = None, vault: dict = None):
        """
        Initialize the storage class with the database connection.

        Args:
            db_connection (object): The database connection object from the psycopg2 library.
            vault (dict): Alternative way to provide the database connection settings. Can't be used with db_connection.
                :param instance (object): The Vault object.
                :param role (str): The database role.

        Example:
            >>> import psycopg2
            >>> conn_pool = psycopg2.pool.SimpleConnectionPool(1, 20, ...)
            >>> db_conn = conn_pool.getconn()
            >>> storage = Storage(db_conn)
            >>> ...
            >>> vault = Vault()
            >>> storage = Storage(vault={'vault': <vault object>, 'role': 'myproject_users'})
        """
        self.db_connection = db_connection
        self.vault = vault
        self.connection = self.create_connection()
        self.cursor = self.connection.cursor()

        if not self.db_connection and not self.vault:
            log.error('[Users]: Failed connection settings. Provide the database connection or vault settings.\ndb_connection: %s\nvault: %s', db_connection, vault)
            raise FailedStorageConnection("Failed to connect to the storage")

        # Test query to check the connection to the database
        try:
            self.cursor.execute("SELECT id FROM users LIMIT 1")
            log.info('[Users]: Successfully connected to the storage %s', self.connection)
        except Exception as error:
            log.error('[Users]: Failed to connect to the storage: %s', error)
            raise FailedStorageConnection("Failed to connect to the storage") from error

    def create_connection(self) -> psycopg2.connect:
        """
        Create a connection for the PostgreSQL database.

        Returns:
            psycopg2.connect: The database connection object.
        """
        if self.vault and not self.db_connection:
            required_keys_configuration = {"host", "port", "dbname"}
            required_keys_credentials = {"username", "password"}
            db_configuration = self.vault['instance'].kv2engine.read_secret(path='configuration/database')
            db_credentials = self.vault['instance'].dbengine.generate_credentials(role=self.vault.get('role', 'undefined'))

            if not db_configuration or not db_credentials:
                raise ValueError('vault: database configuration or credentials are missing')

            missing_keys = (required_keys_configuration - set(db_configuration.keys())) | (required_keys_credentials - set(db_credentials.keys()))
            if missing_keys:
                raise KeyError("vault: missing keys in the database configuration or credentials: {missing_keys}")

            log.info(
                '[Users]: creating a connection for the %s:%s/%s', db_configuration['host'], db_configuration['port'], db_configuration['dbname']
            )
            settings = {
                'host': db_configuration['host'], 'port': db_configuration['port'], 'database': db_configuration['dbname'],
                'user': db_credentials['username'], 'password': db_credentials['password']
            }
            connection = psycopg2.connect(**settings)
        elif self.db_connection and not self.vault:
            connection = self.db_connection
        else:
            raise ValueError('Database connection settings are missing')
        return connection

    @reconnect_on_exception
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

    @reconnect_on_exception
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

    @reconnect_on_exception
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

    @reconnect_on_exception
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
