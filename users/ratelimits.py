"""
This module contains classes and methods for implementing simple request rate limits in Telegram bots.
"""
import random
from datetime import datetime, timedelta
from logger import log
from vault import VaultClient
from constants import VAULT_CONFIG_PATH, VAULT_DATA_PATH


class RateLimiter:
    """
    RateLimiter class provides rate limiting functionality for Telegram bot requests.

    Args:
        :param vault (any): Configuration for initializing the Vault client.
            - (object) VaultClient instance for interacting with the Vault API.
            - (dict) Configuration for initializing a VaultClient instance in this class.
        :param user_id (str): The user ID for which rate limits are applied.

    Returns:
        None

    Attributes:
        _vault (any): The initialized VaultClient instance or None if initialization failed.
        vault_config_path (str): Path to the configuration data in Vault.
        vault_data_path (str): Path to the data in Vault.
        requests_configuration (dict): Configuration for rate limits from Vault.
        requests_counters (dict): Counters for user's requests.
        request_ratelimits (dict): Rate limit information for the user.

    Examples:
        >>> limiter = RateLimiter(vault=vault_client, user_id='12345')
    """
    def __init__(
        self,
        vault: VaultClient = None,
        user_id: str = None
    ) -> None:
        """
        Create a new RateLimiter instance.

        Args:
            :param vault (any): Configuration for initializing the Vault client.
                - (object) VaultClient instance for interacting with the Vault API.
                - (dict) Configuration for initializing a VaultClient instance in this class.
            :param user_id (str): The user ID for which rate limits are applied.

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

        self.user_id = user_id
        self._vault_config_path = VAULT_CONFIG_PATH
        self._vault_data_path = VAULT_DATA_PATH
        self.requests_configuration = self.vault.read_secret(
            path=f"{self.vault_config_path}/{self.user_id}",
            key='requests'
        )

        try:
            self.requests_counters = self.vault.read_secret(
                path=f"{self.vault_data_path}/{user_id}",
                key='requests_counters'
            )
        # pylint: disable=W0718
        # will be fixed after the solution https://github.com/obervinov/vault-package/issues/31
        except Exception:
            self.requests_counters = {'requests_per_day': 0, 'requests_per_hour': 0}

        try:
            self.request_ratelimits = self.vault.read_secret(
                path=f"{self.vault_data_path}/{user_id}",
                key='rate_limits'
            )
        # pylint: disable=W0718
        # will be fixed after the solution https://github.com/obervinov/vault-package/issues/31
        except Exception:
            self.request_ratelimits = {'end_time': None}

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
    def vault_config_path(
        self
    ) -> str:
        """
        Getter for the 'vault_config_path' attribute.

        Returns:
            (str): The 'vault_config_path' attribute.
        """
        return self._vault_config_path

    @vault_config_path.setter
    def vault_config_path(
        self,
        vault_config_path: str = None
    ) -> str:
        """
        Setter for the 'vault_config_path' attribute.

        Args:
            vault_config_path (str): Path to the configuration data in Vault.
        """
        self._vault_config_path = vault_config_path

    @property
    def vault_data_path(
        self
    ) -> str:
        """
        Getter for the 'vault_data_path' attribute.

        Returns:
            (str): The 'vault_data_path' attribute.
        """
        return self._vault_data_path

    @vault_data_path.setter
    def vault_data_path(
        self,
        vault_data_path: str = None
    ) -> str:
        """
        Setter for the 'vault_data_path' attribute.

        Args:
            vault_data_path (str): Path to the data in Vault.
        """
        self._vault_data_path = vault_data_path

    def determine_rate_limit(self) -> dict | None:
        """
        Determine the rate limit status for the user.

        Returns:
            (dict | None): Rate limit information for the user.
            {
              "end_time": "2023-08-07 10:39:00.000000"
            }
                or
            {
              "end_time": None
            }
                or
            None
        """
        # If rate limits already applied
        if self.request_ratelimits['end_time']:
            rate_limits = self.active_rate_limit()

        # If rate limits need to apply
        elif (
            self.requests_configuration['requests_per_day'] <= self.requests_counters['requests_per_day'] or
            self.requests_configuration['requests_per_hour'] <= self.requests_counters['requests_per_hour']
        ):
            rate_limits = self.apply_rate_limit()

        # If no rate limits need to be applied
        elif (
            self.requests_configuration['requests_per_day'] > self.requests_counters['requests_per_day'] and
            self.requests_configuration['requests_per_hour'] > self.requests_counters['requests_per_hour']
        ):
            rate_limits = self.no_active_rate_limit()

        else:
            rate_limits = None

        return rate_limits

    def active_rate_limit(self) -> dict | None:
        """
        Check and handle active rate limits for the user.

        Returns:
            (dict | None): Rate limit information for the user, or None if not active.
            {
              "end_time": "2023-08-07 10:39:00.000000"
            }
                or
            {
              "end_time": None
            }
                or
            None
        """
        if self.request_ratelimits['end_time'] is None:
            return None

        current_time = datetime.now()
        end_time = self.request_ratelimits['end_time']

        if current_time >= datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f'):
            log.info(
                '[class.%s] Date rate limit expired, reset for user ID %s',
                __class__.__name__,
                self.user_id
            )
            self.request_ratelimits['end_time'] = None
            self.vault.write_secret(
                path=f"{self.vault_data_path}/{self.user_id}",
                key='rate_limits',
                value={
                    'end_time': self.request_ratelimits['end_time']
                }
            )
        else:
            log.warning(
                '[class.%s] A speed limit has been detected for user ID %s '
                'that has already been applied and has not expired yet',
                __class__.__name__,
                self.user_id
            )

        return self.request_ratelimits

    def apply_rate_limit(self) -> dict | None:
        """
        Apply rate limits to the user and update counters.

        Returns:
            (dict | None): Rate limit information for the user, or None if not applicable.
            {
              "end_time": "2023-08-07 10:39:00.000000"
            }
                or
            None
        """
        if self.requests_configuration['requests_per_day'] <= self.requests_counters['requests_per_day']:
            log.warning(
                '[class.%s] The request limits are exhausted (per_day), '
                'the rate limit will be applied for user ID %s',
                __class__.__name__,
                self.user_id
            )
            end_time = str(datetime.now() + timedelta(days=1))
            self.request_ratelimits['end_time'] = end_time
            self.requests_counters['requests_per_day'] = 0
            self.requests_counters['requests_per_hour'] = self.requests_counters['requests_per_hour'] + 1
            log.info(
                '[class.%s] Rate limit for user ID %s set to expire at %s',
                __class__.__name__,
                self.user_id,
                end_time
            )

        elif self.requests_configuration['requests_per_hour'] <= self.requests_counters['requests_per_hour']:
            log.warning(
                '[class.%s] The request limits are exhausted (per_hour), '
                'the rate limit will be applied for user ID %s',
                __class__.__name__,
                self.user_id
            )
            shift_minutes = random.randint(1, self.requests_configuration['random_shift_minutes'])
            end_time = str(
                datetime.now() + timedelta(
                    hours=1,
                    minutes=shift_minutes
                )
            )
            self.request_ratelimits['end_time'] = end_time
            self.requests_counters['requests_per_hour'] = 0
            self.requests_counters['requests_per_day'] = self.requests_counters['requests_per_day'] + 1

            log.info(
                '[class.%s] Rate limit for user ID %s set to expire at %s',
                __class__.__name__,
                self.user_id,
                end_time
            )

        self.vault.write_secret(
            path=f"{self.vault_data_path}/{self.user_id}",
            key='requests_counters',
            value=self.requests_counters
        )
        self.vault.write_secret(
            path=f"{self.vault_data_path}/{self.user_id}",
            key='rate_limits',
            value=self.request_ratelimits
        )
        return self.request_ratelimits

    def no_active_rate_limit(self) -> dict:
        """
        Handle the case when no rate limits are applicable.

        Returns:
            (dict): Rate limit information for the user, or None if no limits needed.
            {
                'end_time': None
            }
        """
        log.info(
            '[class.%s] The limits have not been exhausted, '
            'the limits on the number of requests are not applied for user ID %s',
            __class__.__name__,
            self.user_id
        )
        updated_counters = self.requests_counters.copy()
        updated_counters['requests_per_day'] += 1
        updated_counters['requests_per_hour'] += 1

        self.vault.write_secret(
            path=f"{self.vault_data_path}/{self.user_id}",
            key='requests_counters',
            value=updated_counters
        )

        return {
            'end_time': None
        }
