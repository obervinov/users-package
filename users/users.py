"""
This python module is a implementation of user management functionality for telegram bots, such as:
authentication, authorization and request limiting.
"""
import json
from logger import log
from vault import VaultClient
from .constants import USERS_VAULT_CONFIG_PATH, USER_STATUS_ALLOW, USER_STATUS_DENY
from .ratelimits import RateLimiter
from .storage import Storage
from .exceptions import VaultInstanceNotSet


class Users:
    """
    This class provides authentication, authorization, and user attribute management
    for Telegram bots.

    Args:
        :param vault (any): Configuration for initializing the Vault client.
            - (object) VaultClient instance for interacting with the Vault API.
            - (dict) Configuration for initializing a VaultClient instance in this class.
        :param rate_limits (bool): Enable rate limit functionality. Default is False.

    Attributes:
        vault (any): The initialized VaultClient instance or None if initialization failed.
        rate_limits (bool): Enable or disable rate limit functionality.
        user_status_allow (str): A constant representing allowed user status.
        user_status_deny (str): A constant representing denied user status.
        vault_config_path (str): Path to the configuration data in Vault.

    Raises:
        VaultInstanceNotSet: If the vault instance is not set.

    Examples:
        >>> users_with_ratelimits = Users(vault=vault_client, rate_limits=True)

        >>> users = Users(vault=vault_client)

        >>> vault_config = {
                "namespace": "my_project",
                "url": "https://vault.example.com",
                "auth": {
                    "type": "approle",
                    "role_id": "role_id",
                    "secret_id": "secret_id"
                }
           }
        >>> users_with_dict_vault = Users(vault=vault_config)
    """
    def __init__(
        self,
        vault: any = None,
        rate_limits: bool = False
    ) -> None:
        """
        Create a new Users instance.

        Args:
            :param vault (any): Configuration for initializing the Vault client.
                - (object) VaultClient instance for interacting with the Vault API.
                - (dict) Configuration for initializing a VaultClient instance in this class.
            :param rate_limits (bool): Enable rate limit functionality. Default is False.

        Raises:
            VaultInstanceNotSet: If the vault instance is not set.

        Returns:
            None

        See the class docstring for more details and examples.
        """
        if isinstance(vault, VaultClient):
            self.vault = vault
        elif isinstance(vault, dict):
            self.vault = VaultClient(
                url=vault.get('url', None),
                namespace=vault.get('namespace', None),
                auth=vault.get('auth', None)
            )
        else:
            log.error('[Users]: wrong vault parameters in Users(vault=%s), see doc-string', vault)
            raise VaultInstanceNotSet("Vault instance is not set. Please provide a valid Vault instance as instance or dictionary.")

        self.rate_limits = rate_limits
        self.storage = Storage(vault_client=self.vault)
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
            :param chat_id (str): Required chat ID.
            :param message_id (str): Required message ID.

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
                'rate_limits': {
                    'end_time': '2023-08-06 11:47:09.440933'
                }
            }
                or
            (dict) {
                'access': self.user_status_allow / self.user_status_deny,
                'permissions': self.user_status_allow / self.user_status_deny,
                'rate_limits': {
                    'end_time': None,
                }
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

        if user_info['access'] == self.user_status_allow:
            self.storage.register_user(
                user_id=user_id,
                status=user_info['access'],
                chat_id=kwargs.get('chat_id', 'undefined')
            )

            if role_id:
                user_info['permissions'] = self._authorization(
                    user_id=user_id,
                    role_id=role_id
                )
                if user_info['permissions'] == self.user_status_allow and self.rate_limits:
                    rl_controller = RateLimiter(
                        vault=self.vault,
                        storage=self.storage,
                        user_id=user_id
                    )
                    user_info['rate_limits'] = rl_controller.determine_rate_limit()

        self.storage.log_user_request(
            user_id=user_id,
            request={
                'chat_id': kwargs.get('chat_id', 'undefined'),
                'message_id': kwargs.get('message_id', 'undefined'),
                'authentication': user_info['access'],
                'authorization': {'role_id': role_id, 'status': user_info.get('permissions', 'undefined')},
                'rate_limits': user_info.get('rate_limits', 'undefined')
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
        roles = self.vault.read_secret(
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
