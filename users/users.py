"""
This python module is a simple implementation of user management functionality for telegram bots, such as:
authentication, authorization and request limiting.
"""
from datetime import datetime
from logger import log
from vault import VaultClient
from constants import VAULT_CONFIG_PATH, VAULT_DATA_PATH, USER_STATUS_ALLOW, USER_STATUS_DENY
from ratelimits import RateLimiter


class Users:
    """
    This class provides authentication, authorization, and user attribute management
    for Telegram bots.

    Args:
        :param vault (any): Configuration for initializing the Vault client.
            - (object) VaultClient instance for interacting with the Vault API.
            - (dict) Configuration for initializing a VaultClient instance in this class.

        :param rate_limits (bool): Enable rate limit functionality.

    Returns:
        None

    Attributes:
        vault (any): The initialized VaultClient instance or None if initialization failed.
        rate_limits (bool): Enable or disable rate limit functionality.
        user_status_allow (str): A constant representing allowed user status.
        user_status_deny (str): A constant representing denied user status.
        vault_config_path (str): Path to the configuration data in Vault.
        vault_data_path (str): Path to the data in Vault.

    Examples:
        >>> users_without_ratelimits = Users(vault=vault_client, rate_limits=False)

        >>> users_with_ratelimits = Users(vault=vault_client)

        >>> vault_config = {
                "name": "my_project",
                "url": "https://vault.example.com",
                "approle": {
                    "id": "my_approle",
                    "secret-id": "my_secret"
                }
           }
        >>> users_with_dict_vault = Users(vault=vault_config)
    """

    def __init__(
        self,
        vault: any = None,
        rate_limits: bool = True
    ) -> None:
        """
        Create a new Users instance.

        Args:
            :param vault (any): Configuration for initializing the vault client.
                :param vault (object): VaultClient instance for interacting with the Vault API.
                :param vault (dict): Configuration for initializing a VaultClient instance in this class.
                    - name (str): Name of the individual mount point of your project.
                    - url (str): URL to the vault server.
                    - approle (dict): Configuration for the AppRole authentication method.
                        - id (str): The identifier of the AppRole.
                        - secret-id (str): Secret ID for the AppRole.

            :param rate_limits (bool): Enable rate limit functionality.

        Returns:
            None

        See the class docstring for more details and examples.
        """
        if isinstance(vault, VaultClient):
            self._vault = vault
        elif isinstance(vault, dict):
            self._vault = VaultClient(
                name=vault.get('name', None),
                url=vault.get('url', None),
                approle=vault.get('approle', None)
            )
        else:
            log.error(
                '[class.%s] wrong vault parameters in Users(vault=%s), see doc-string',
                __class__.__name__,
                vault
            )
            self._vault = None

        self.rate_limits = rate_limits
        self._user_status_allow = USER_STATUS_ALLOW
        self._user_status_deny = USER_STATUS_DENY
        self._vault_config_path = VAULT_CONFIG_PATH
        self._vault_data_path = VAULT_DATA_PATH

    @property
    def vault(self):
        """
        Getter for the 'vault' attribute.

        Returns:
            (any): The 'vault' attribute.
        """
        return self._vault

    @vault.setter
    def vault(self, vault: any):
        """
        Setter for the 'vault' attribute.

        Args:
            vault (any): Configuration for initializing the Vault client.
        """
        if isinstance(vault, VaultClient):
            self._vault = vault
        elif isinstance(vault, dict):
            self._vault = VaultClient(
                name=vault.get('name', None),
                url=vault.get('url', None),
                approle=vault.get('approle', None)
            )
        else:
            log.error(
                '[class.%s] wrong vault parameters in Users(vault=%s), see doc-string',
                __class__.__name__,
                vault
            )
            self._vault = None

    @property
    def user_status_allow(self):
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
    def user_status_deny(self):
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
    def vault_config_path(self):
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

    @property
    def vault_data_path(self):
        """
        Getter for the 'vault_data_path' attribute.

        Returns:
            (str): The 'vault_data_path' attribute.
        """
        return self._vault_data_path

    @vault_data_path.setter
    def vault_data_path(self, vault_data_path: str):
        """
        Setter for the 'vault_data_path' attribute.

        Args:
            vault_data_path (str): Path to the data in Vault.
        """
        self._vault_data_path = vault_data_path

    def user_access_check(
        self,
        user_id: str = None,
        role_id: str = None
    ) -> dict:
        """
        The main entry point for authentication, authorization, and request rate limit verification.

        Args:
            :param user_id (str): Required user ID.
            :param role_id (str): Required role ID for the specified user ID.

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
                    role_id='admin_role'
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

        user_info['access'] = self.authentication(
            user_id=user_id
        )
        if user_info['access'] == self.user_status_allow and role_id:
            user_info['permissions'] = self.authorization(
                user_id=user_id,
                role_id=role_id
            )
            if user_info['permissions'] == self.user_status_allow and self.rate_limits:
                rl_controller = RateLimiter(
                    vault=self.vault,
                    user_id=user_id
                )
                user_info['rate_limits'] = rl_controller.determine_rate_limit()

        return user_info

    def authentication(
        self,
        user_id: str = None
    ) -> str:
        """
        Checks if the specified user ID has access to the bot.

        Args:
            :param user_id (str): Required user ID.

        Examples:
          >>> authentication(
                user_id='user1'
              )

        Returns:
            (str) self.user_status_allow
                or
            (str) self.user_status_deny
        """
        try:
            status = self.vault.read_secret(
                path=f"{self.vault_config_path}/{user_id}",
                key='status'
            )
        # pylint: disable=W0718
        # will be fixed after the solution https://github.com/obervinov/vault-package/issues/31
        except Exception:
            status = self.user_status_deny

        log.info(
            '[class.%s] Access from user ID %s: %s',
            __class__.__name__,
            user_id,
            status
        )
        self.vault.write_secret(
            path=f"{self.vault_data_path}/{user_id}",
            key='authentication',
            value={
                'time': str(datetime.now()),
                'status': status
            }
        )
        return status

    def authorization(
        self,
        user_id: str = None,
        role_id: str = None
    ) -> str:
        """
        Methods for checking whether the user has the specified role.

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
        try:
            if role_id in self.vault.read_secret(
                path=f"{self.vault_config_path}/{user_id}",
                key='roles'
            ):
                status = self.user_status_allow
            else:
                status = self.user_status_deny
        # pylint: disable=W0718
        # will be fixed after the solution https://github.com/obervinov/vault-package/issues/31
        except Exception:
            status = self.user_status_deny

        log.info(
            '[class.%s] User ID %s has the role %s: %s',
            __class__.__name__,
            user_id,
            role_id,
            status
        )
        self.vault.write_secret(
            path=f"{self.vault_data_path}/{user_id}",
            key='authorization',
            value={
                'time': str(datetime.now()),
                'status': status,
                'role': role_id
            }
        )
        return status
