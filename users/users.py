"""
This python module is a implementation of user management functionality for telegram bots, such as:
authentication, authorization and request limiting.
"""
import json
from logger import log
from vault import VaultClient
from .constants import USERS_VAULT_CONFIG_PATH, USER_STATUS_ALLOW, USER_STATUS_DENY
from .ratelimiter import RateLimiter
from .storage import Storage
from .exceptions import VaultInstanceNotSet


class Users:
    """
    This class provides authentication, authorization, and user attribute management
    for Telegram bots.

    Attributes:
        vault (any): The Vault client instance for interacting with the Vault API. It can be an object or a dictionary.
        storage (Storage): The storage object for interacting with the database.
        rate_limits (bool): Enable or disable rate limit functionality.
        user_status_allow (str): A constant representing allowed user status.
        user_status_deny (str): A constant representing denied user status.
        vault_config_path (str): Path to the configuration data in Vault.

    Methods:
        access_control: Acts as a decorator factory for access control.
        user_access_check: The main entry point for authentication, authorization, and request rate limit verification.
        _authentication: Checks if the specified user ID has access to the bot.
        _authorization: Checks if the specified user ID has the specified role.

    Raises:
        VaultInstanceNotSet: If the vault instance is not set.
    """
    def __init__(
        self,
        vault: any = None,
        rate_limits: bool = False,
        storage_connection: any = None
    ) -> None:
        """
        Create a new Users instance.

        Args:
            :param vault (any): configuration or instance of VaultClient for interacting with the Vault API.
                - (object) already initialized VaultClient instance.
                - (dict) extended configuration for VaultClient (for database engine).
                    :param instance (object): The already initialized VaultClient instance.
                    :param role (str): The role name for the database engine in Vault.
            :param rate_limits (bool): Enable rate limit functionality. Default is False.
            :param storage_connection (any): Connection object to connect to the storage. Do not use if you are using Vault database engine.

        Examples:
            >>> import psycopg2
            >>> conn_pool = psycopg2.pool.SimpleConnectionPool(1, 20, ...)
            >>> db_conn = conn_pool.getconn()
            >>> users_with_ratelimits = Users(vault=<VaultClient>, rate_limits=True, storage_connection=db_conn)
            >>> users = Users(vault=<VaultClient>, storage_connection=db_conn)
            >>> ...
            >>> vault_dict = {
            >>>     'instance': <vault_object>,
            >>>     'role': 'myproject-dbengine-role'
            >>> }
            >>> users_with_dbengine = Users(vault=vault_dict)
        """
        if isinstance(vault, VaultClient):
            self.vault = vault
            self.storage = Storage(db_connection=storage_connection)
        elif isinstance(vault, dict):
            self.vault = vault.get('instance', None)
            self.storage = Storage(vault=vault)
        else:
            log.error('[Users]: wrong vault parameters in Users(vault=%s), see doc-string', vault)
            raise VaultInstanceNotSet("Vault instance is not set. Please provide a valid Vault instance as instance or dictionary.")

        self.rate_limits = rate_limits
        self._user_status_allow = USER_STATUS_ALLOW
        self._user_status_deny = USER_STATUS_DENY
        self._vault_config_path = USERS_VAULT_CONFIG_PATH

    @property
    def user_status_allow(self) -> str:
        """
        Getter for the 'user_status_allow' attribute.

        Returns:
            (str): The 'user_status_allow' attribute.
        """
        return self._user_status_allow

    @user_status_allow.setter
    def user_status_allow(self, user_status_allow: str):
        """
        Setter for the 'user_status_allow' attribute.

        Args:
            user_status_allow (str): User status for allowed access.
        """
        self._user_status_allow = user_status_allow

    @property
    def user_status_deny(self) -> str:
        """
        Getter for the 'user_status_deny' attribute.

        Returns:
            (str): The 'user_status_deny' attribute.
        """
        return self._user_status_deny

    @user_status_deny.setter
    def user_status_deny(self, user_status_deny: str):
        """
        Setter for the 'user_status_deny' attribute.

        Args:
            user_status_deny (str): User status for denied access.
        """
        self._user_status_deny = user_status_deny

    @property
    def vault_config_path(self) -> str:
        """
        Getter for the 'vault_config_path' attribute.

        Returns:
            (str): The 'vault_config_path' attribute.
        """
        return self._vault_config_path

    @vault_config_path.setter
    def vault_config_path(self, vault_config_path: str):
        """
        Setter for the 'vault_config_path' attribute.

        Args:
            vault_config_path (str): Path to the configuration data in Vault.
        """
        self._vault_config_path = vault_config_path

    def access_control(self, role_id: str = None, flow: str = 'auth'):
        """
        Instance method that acts as a decorator factory for access control.
        Working with the pyTelegramBotAPI objects: telegram.telegram_types.Message or telegram.telegram_types.CallbackQuery.

        Args:
            role_id (str): The role to check against.
            flow (str): The type of access control:
                - 'auth': Authentication.
                - 'authz': Authorization.
        Returns:
            function: The decorator.

        Examples:
            >>> @telegram.message_handler(commands=['start'])
            >>> @access_control(role_id='admin_role', flow='authz')
                def my_function(message: telegram.telegram_types.Message, access_result: dict = None):
                    print(f"User permissions: {access_result}")
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Check if the first argument is an object (message or call)
                obj = args[0] if args else None
                # Extract user_id, chat_id, and message_id from the object
                if hasattr(obj, 'message'):  # from call
                    obj = obj.message
                if hasattr(obj, 'chat'):  # from message
                    resolved_user_id = obj.chat.id
                    resolved_chat_id = obj.chat.id
                    resolved_message_id = obj.message_id
                else:
                    log.error('[Users]: unsupported object type for access control: %s (%s)', obj, type(obj))
                    raise ValueError("Unsupported object type for access control.")

                access_result = self.user_access_check(
                    user_id=resolved_user_id, role_id=role_id,
                    chat_id=resolved_chat_id, message_id=resolved_message_id
                )
                access_allowed = (
                    (flow == 'auth' and access_result.get('access') == self.user_status_allow) or
                    (flow == 'authz' and access_result.get('permissions') == self.user_status_allow)
                )
                if access_allowed:
                    kwargs['access_result'] = access_result
                    return func(*args, **kwargs)
                return None
            return wrapper
        return decorator

    def user_access_check(
        self,
        user_id: str = None,
        role_id: str = None,
        **kwargs
    ) -> dict:
        """
        The main entry point for authentication, authorization, and request rate limit verification.

        Args:
            :param user_id (str): Required user ID.
            :param role_id (str): Required role ID for the specified user ID.

        Keyword Args:
            :param chat_id (str): Required chat ID. Additional information for logging.
            :param message_id (str): Required message ID. Additional information for logging.

        Returns:
            (dict) {
                'access': self.user_status_allow / self.user_status_deny
            }
                or
            (dict) {
                'access': self.user_status_allow / self.user_status_deny,
                'permissions': self.user_status_allow / self.user_status_deny
            }
                or
            (dict) {
                'access': self.user_status_allow / self.user_status_deny,
                'permissions': self.user_status_allow / self.user_status_deny,
                'rate_limits': 2023-08-06 11:47:09.440933
            }
                or
            (dict) {
                'access': self.user_status_allow / self.user_status_deny,
                'permissions': self.user_status_allow / self.user_status_deny,
                'rate_limits': None
            }

        Examples:
            >>> user_access_check(
                    user_id='user1',
                    role_id='admin_role',
                    chat_id='chat1',
                    message_id='msg1'
                )

        This method serves as the main entry point for user access control.
        It first performs user authentication and then,
        if the user is authenticated and a role ID is provided,
        it checks for user authorization. If rate limits are enabled,
        it also verifies request rate limits for the user.
        The function returns a dictionary containing information about access, permissions, and rate limits
        if applicable.
        """
        user_info = {}
        user_info['access'] = self._authentication(user_id=user_id)
        self.storage.register_user(user_id=user_id, status=user_info['access'], chat_id=kwargs.get('chat_id', 'unknown'))

        if user_info['access'] == self.user_status_allow and role_id:
            user_info['permissions'] = self._authorization(user_id=user_id, role_id=role_id)

            if user_info['permissions'] == self.user_status_allow and self.rate_limits:
                rl_controller = RateLimiter(vault=self.vault, storage=self.storage, user_id=user_id)
                user_info['rate_limits'] = rl_controller.determine_rate_limit()

        self.storage.log_user_request(
            user_id=user_id,
            request={
                'chat_id': kwargs.get('chat_id', 'undefined'),
                'message_id': kwargs.get('message_id', 'undefined'),
                'authentication': user_info['access'],
                'authorization': {'role_id': role_id, 'status': user_info.get('permissions', 'undefined')},
                'rate_limits': user_info.get('rate_limits', None)
            }
        )
        return user_info

    def _authentication(
        self,
        user_id: str = None
    ) -> str:
        """
        Checks if the specified user ID has access to the bot.

        Args:
            :param user_id (str): Required user ID.

        Examples:
          >>> authentication(
                user_id='User1'
              )

        Returns:
            (str) self.user_status_allow
                or
            (str) self.user_status_deny
        """
        status = self.vault.kv2engine.read_secret(
            path=f"{self.vault_config_path}/{user_id}",
            key='status'
        )
        # verification of the status value
        if status is None:
            log.info('[Users]: user ID %s not found in Vault configuration and will be denied access', user_id)
            status = self.user_status_deny
        elif status in self.user_status_allow or status in self.user_status_deny:
            log.info('[Users]: access from user ID %s: %s', user_id, status)
        else:
            log.error(
                '[Users] invalid configuration for %s status=%s value can be %s or %s',
                user_id, status, self.user_status_allow, self.user_status_deny
            )
            status = self.user_status_deny
        return status

    def _authorization(
        self,
        user_id: str = None,
        role_id: str = None
    ) -> str:
        """
        Checking whether the user has the specified role.

        Args:
            :param user_id (str): Required user ID.
            :param role_id (str): Required role ID for the specified user ID.

        Examples:
          >>> authorization(
                user_id='user1',
                role_id='admin_role'
              )

        Returns:
            (str) self.user_status_allow
                or
            (str) self.user_status_deny
        """
        roles = self.vault.kv2engine.read_secret(
            path=f"{self.vault_config_path}/{user_id}",
            key='roles'
        )
        if roles:
            if role_id in json.loads(roles):
                status = self.user_status_allow
            else:
                status = self.user_status_deny
        else:
            status = self.user_status_deny
        log.info('[Users]: check role `%s` for user `%s`: %s', role_id, user_id, status)
        return status
