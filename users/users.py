"""
This python module is a implementation of user management functionality for telegram bots, such as:
authentication, authorization and request limiting.
"""
import json
import secrets
import hashlib
from datetime import datetime, timedelta
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

    def issue_token(
        self,
        user_id: str = None,
        ttl_minutes: int = 10
    ) -> str:
        """
        Generate a temporary access token for the specified user.

        Args:
            :param user_id (str): User ID to issue token for.
            :param ttl_minutes (int): Token validity period in minutes (default 10).

        Returns:
            (str | None): Token in format "user_id.token_id" or None if token could not be stored (e.g., tokens table missing)

        Raises:
            ValueError: If user_id is not provided.

        Examples:
            >>> users = Users(vault=<VaultClient>, storage_connection=db_conn)
            >>> token = users.issue_token(user_id='user1', ttl_minutes=15)
            >>> print(token)
            'user1.a8f3kjs9dfjkl23jrlksjdf...'
        """
        if not user_id:
            log.error('[Users]: user_id is required for token issuance')
            raise ValueError("user_id is required for token issuance")

        if '.' in str(user_id):
            log.error('[Users]: user_id cannot contain period characters (breaks token format)')
            raise ValueError("user_id cannot contain period characters")

        # Generate token components
        token_id = secrets.token_urlsafe(32)
        token_salt = secrets.token_hex(32)
        token_hash = hashlib.pbkdf2_hmac('sha256', token_id.encode(), token_salt.encode(), 100_000).hex()

        # Calculate expiration
        expires_at = datetime.now() + timedelta(minutes=ttl_minutes)

        # Store token in database
        store_result = self.storage.store_token(
            user_id=user_id,
            token_hash=token_hash,
            token_salt=token_salt,
            expires_at=expires_at
        )

        if store_result is False:
            log.warning('[Users]: Token storage skipped; tokens table missing. Returning None for backward compatibility.')
            return None

        # Return plaintext token
        token = f"{user_id}.{token_id}"
        log.info('[Users]: Token issued for user %s (expires at %s)', user_id, expires_at)
        return token

    def validate_token(
        self,
        token: str = None
    ) -> dict:
        """
        Validate a token and return user information.

        Args:
            :param token (str): Token string in format "user_id.token_id"

        Returns:
            (dict | None): User info {'user_id', 'status', 'roles'} if valid; None if token is invalid, expired, used, or missing

        Raises:
            ValueError: If token format is invalid.

        Examples:
            >>> users = Users(vault=<VaultClient>, storage_connection=db_conn)
            >>> user_info = users.validate_token(token='user1.a8f3kjs9dfjkl23jrlksjdf...')
            >>> if user_info:
            >>>     print(f"User: {user_info['user_id']}, Status: {user_info['status']}")
        """
        if not token or '.' not in token:
            log.error('[Users]: Invalid token format')
            raise ValueError("Invalid token format. Expected format: 'user_id.token_id'")

        # Parse token
        user_id, token_id = token.split('.', 1)

        # Retrieve stored token data
        token_data = self.storage.get_token(user_id=user_id)

        if not token_data:
            log.warning('[Users]: No valid token found for user %s', user_id)
            return None

        # Verify token hash
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            token_id.encode(),
            token_data['token_salt'].encode(),
            100_000
        ).hex()

        if not secrets.compare_digest(computed_hash, token_data['token_hash']):
            log.warning('[Users]: Token validation failed for user %s (hash mismatch)', user_id)
            return None

        # Mark token as used (single-use enforcement)
        self.storage.mark_token_used(user_id=user_id)

        # Retrieve user configuration from Vault in a single call
        user_config = self.vault.kv2engine.read_secret(path=f"{self.vault_config_path}/{user_id}") or {}
        user_status = user_config.get('status')
        user_roles = user_config.get('roles')

        user_info = {
            'user_id': user_id,
            'status': user_status if user_status else self.user_status_deny,
            'roles': json.loads(user_roles) if user_roles else []
        }

        log.info('[Users]: Token validated successfully for user %s', user_id)
        return user_info

    def revoke_token(
        self,
        user_id: str = None
    ) -> None:
        """
        Revoke any existing token for the specified user.

        Args:
            :param user_id (str): User ID to revoke token for.

        Raises:
            ValueError: If user_id is not provided.

        Examples:
            >>> users = Users(vault=<VaultClient>, storage_connection=db_conn)
            >>> users.revoke_token(user_id='user1')
        """
        if not user_id:
            log.error('[Users]: user_id is required for token revocation')
            raise ValueError("user_id is required for token revocation")

        if '.' in str(user_id):
            log.error('[Users]: user_id cannot contain period characters (breaks token format)')
            raise ValueError("user_id cannot contain period characters")

        # Mark all active tokens as used
        self.storage.mark_token_used(user_id=user_id)
        log.info('[Users]: All tokens revoked for user %s', user_id)
