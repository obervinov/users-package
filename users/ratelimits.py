# pylint: disable=R0801
"""
This module provides the rate limit functionality for requests to the Telegram bot.
"""
import random
import json
from json.decoder import JSONDecodeError
from typing import Union
from datetime import datetime, timedelta
from logger import log
from vault import VaultClient
from .constants import VAULT_CONFIG_PATH, VAULT_DATA_PATH
from .exceptions import WrongUserConfiguration, VaultInstanceNotSet, FailedDeterminateRateLimit


# pylint: disable=too-many-instance-attributes
class RateLimiter:
    """
    The RateLimiter class provides the rate limit functionality for requests
    to the Telegram bot in the context of a specific user.

    Args:
        :param vault (any): Configuration for initializing the Vault client.
            - (object) VaultClient instance for interacting with the Vault API.
            - (dict) Configuration for initializing a VaultClient instance in this class.

        :param user_id (str): User ID for checking rate limits.

    Returns:
        None

    Attributes:
        vault (any): The initialized VaultClient instance or None if initialization failed.
        vault_config_path (str): Path to the configuration data in Vault.
        vault_data_path (str): Path to the historical data in Vault.
        requests_configuration (dict): Configuration for rate limits from Vault.
        requests_counters (dict): Counters for user's requests.
        requests_ratelimits (dict): Rate limit information for the user.

    Raises:
        VaultInstanceNotSet: If the Vault instance is not set.
        WrongUserConfiguration: If the user configuration in Vault is wrong.
        FailedDeterminateRateLimit: If the rate limit for the user ID cannot be determined.

    Examples:
        >>> limiter = RateLimiter(vault=vault_client, user_id='User1')
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

            :param user_id (str): User ID for checking rate limits.

        Returns:
            None

        Raises:
            VaultInstanceNotSet: If the Vault instance is not set.
            WrongUserConfiguration: If the user configuration in Vault is wrong.

        See the class docstring for more details and examples.
        """
        # Initialize the Vault client
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
            raise VaultInstanceNotSet("Vault instance is not set. Please provide a valid Vault instance as instance or dictionary.")

        # Initialize the user ID and constants
        self.user_id = user_id
        self._vault_config_path = VAULT_CONFIG_PATH
        self._vault_data_path = VAULT_DATA_PATH

        # Read general user configuration from Vault
        user_configuration = self.vault.read_secret(
            path=f"{self.vault_config_path}/{self.user_id}"
        )
        # Extract requests configuration from general user configuration
        requests_configuration = user_configuration.get('requests', None)
        if requests_configuration:
            try:
                self.requests_configuration = json.loads(requests_configuration)
            except (TypeError, JSONDecodeError) as error:
                log.error(
                    '[class.%s] Wrong value for requests configuration for user ID %s: %s',
                    __class__.__name__,
                    self.user_id,
                    error
                )
                raise WrongUserConfiguration("User configuration in Vault is wrong. Please provide a valid configuration for requests.") from error
        else:
            log.error(
                '[class.%s] No requests configuration found for user ID %s',
                __class__.__name__,
                self.user_id
            )
            raise WrongUserConfiguration("User configuration in Vault is wrong. Please provide a valid configuration for rate limits.")

        # Read general dynamic user data from Vault
        user_data = self.vault.read_secret(
            path=f"{self.vault_data_path}/{user_id}"
        )
        # Extract requests counters from general dynamic user data
        requests_counters = user_data.get(
            'requests_counters',
            '{"requests_per_day": 0, "requests_per_hour": 0}'
        )
        try:
            self.requests_counters = json.loads(requests_counters)
        except (TypeError, JSONDecodeError) as error:
            log.error(
                '[class.%s] Wrong value for requests counters for user ID %s: %s',
                __class__.__name__,
                self.user_id,
                error
            )
            raise WrongUserConfiguration("User data in Vault is wrong. Please provide a valid configuration for requests.") from error
        # Extract rate limit timestamp from general dynamic user data
        requests_ratelimits = user_data.get(
            'requests_ratelimits',
            '{"end_time": null}'
        )
        try:
            self.requests_ratelimits = json.loads(requests_ratelimits)
        except (TypeError, JSONDecodeError) as error:
            log.error(
                '[class.%s] Wrong value for rate limits for user ID %s: %s',
                __class__.__name__,
                self.user_id,
                error
            )
            raise WrongUserConfiguration("User data in Vault is wrong. Please check user dynamic data.") from error
        # Extract historical requests from general dynamic user data
        requests_history = user_data.get(
            'requests_history',
            '[]'
        )
        try:
            self.requests_history = json.loads(requests_history)
        except (TypeError, JSONDecodeError) as error:
            log.error(
                '[class.%s] Wrong value for historical requests for user ID %s: %s',
                __class__.__name__,
                self.user_id,
                error
            )
            raise WrongUserConfiguration("User data in Vault is wrong. Please check user dynamic data.") from error

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
        self._vault = vault

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

    def determine_rate_limit(self) -> Union[dict, None]:
        """
        Determine the rate limit status for the user ID.

        Args:
            None

        Raises:
            FailedDeterminateRateLimit: If the rate limit for the user ID cannot be determined.

        Examples:
            >>> rl_status = limiter.determine_rate_limit()

        Returns:
            (dict | None): Rate limit timestamp for the user ID.
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
        log.debug(
            'Before determining the rate limit status\nConfiguration: %s\nHistory: %s\nCounters: %s\n',
            self.requests_configuration,
            self.requests_history,
            self.requests_counters
        )
        # update the request counters based on the configured rate limits
        self._update_requests_counters()
        # If rate limits already applied
        if self.requests_ratelimits['end_time']:
            rate_limits = self._active_rate_limit()
        # If rate limits need to apply
        elif (
            self.requests_configuration['requests_per_day'] <= self.requests_counters['requests_per_day'] or
            self.requests_configuration['requests_per_hour'] <= self.requests_counters['requests_per_hour']
        ):
            rate_limits = self._apply_rate_limit()
        # If no rate limits, just +1 to request counters
        elif (
            self.requests_configuration['requests_per_day'] > self.requests_counters['requests_per_day'] and
            self.requests_configuration['requests_per_hour'] > self.requests_counters['requests_per_hour']
        ):
            rate_limits = {'end_time': None}
        # If something went wrong
        else:
            log.error(
                '[class.%s] Failed to determinate rate limit for user ID %s:\nConfiguration: %s\nCounters: %s\nHistory: %s\n',
                __class__.__name__,
                self.user_id,
                self.requests_configuration,
                self.requests_counters,
                self.requests_history
            )
            raise FailedDeterminateRateLimit("Failed to determinate rate limit for the user ID.")
        # update the request history for the user ID with current request timestamp
        self._update_requests_history()
        log.debug(
            'After determining the rate limit status\nCounters: %s\nRateLimits: %s\nConfig: %s\n',
            self.requests_counters,
            self.requests_ratelimits,
            self.requests_configuration
        )
        return {'end_time': rate_limits['end_time'] if rate_limits else None}

    def _update_requests_history(self) -> None:
        """
        Update the request history for the user ID.

        Args:
            None

        Returns:
            None

        Raises:
            WrongUserConfiguration: If the user data in Vault is wrong.

        Examples:
            >>> limiter._update_requests_history()
        """
        request_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            self.requests_history.append(request_timestamp)
            self.requests_history.sort()
        except (TypeError, JSONDecodeError) as error:
            log.error(
                '[class.%s] Wrong value for requests history for user ID %s: %s',
                __class__.__name__,
                self.user_id,
                error
            )
            raise WrongUserConfiguration("User data in Vault is wrong. Please check user dynamic data.") from error
        # Update the request history in Vault
        self.vault.write_secret(
            path=f"{self.vault_data_path}/{self.user_id}",
            key='requests_history',
            value=json.dumps(self.requests_history)
        )

    def _active_rate_limit(self) -> Union[dict, None]:
        """
        Check and handle active rate limits for the user ID.

        Args:
            None

        Returns:
            (dict | None): Rate limit timestamp for the user ID or None if the time has already expired.
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
        if self.requests_ratelimits['end_time'] is None:
            return None

        if datetime.now() >= datetime.strptime(self.requests_ratelimits['end_time'], '%Y-%m-%d %H:%M:%S.%f'):
            log.info(
                '[class.%s] Rate limit for user ID %s has expired, resetting the rate limit',
                __class__.__name__,
                self.user_id
            )
            self.requests_ratelimits['end_time'] = None
            self.vault.write_secret(
                path=f"{self.vault_data_path}/{self.user_id}",
                key='requests_ratelimits',
                value=json.dumps(self.requests_ratelimits)
            )
        else:
            log.warning(
                '[class.%s] A rate limit has been detected for user ID %s '
                'that has already been applied and has not expired yet',
                __class__.__name__,
                self.user_id
            )

            # Calculate the multiplier on the rate limit if requests continue to arrive after the application of rate_limit
            # in order to distribute the remaining requests in the same way based on the configuration

            # Situation 1: counter exceeds configuration and configuration equals 1
            if (
                self.requests_configuration['requests_per_hour'] == 1
                and
                self.requests_counters['requests_per_hour'] > self.requests_configuration['requests_per_hour']
            ):
                shift_minutes = 60 + random.randint(1, self.requests_configuration['random_shift_minutes'])

            # Situation 2: counter exceeds configuration by a multiple
            elif (
                self.requests_counters['requests_per_hour'] > self.requests_configuration['requests_per_hour']
                and
                self.requests_counters['requests_per_hour'] % self.requests_configuration['requests_per_hour'] == 0
            ):
                shift_minutes = 60 + random.randint(1, self.requests_configuration['random_shift_minutes'])

            # Situation 3: counter exceeds configuration, but not by a multiple
            elif (
                self.requests_counters['requests_per_hour'] > self.requests_configuration['requests_per_hour']
                and
                self.requests_counters['requests_per_hour'] % self.requests_configuration['requests_per_hour'] != 0
            ):
                shift_minutes = random.randint(1, self.requests_configuration['random_shift_minutes'])

            # Situation 4: counter does not exceed configuration
            else:
                shift_minutes = 0

            latest_end_time = datetime.strptime(
                self.requests_ratelimits['end_time'],
                '%Y-%m-%d %H:%M:%S.%f'
            )
            self.requests_ratelimits['end_time'] = str(latest_end_time + timedelta(minutes=shift_minutes))
            self.vault.write_secret(
                path=f"{self.vault_data_path}/{self.user_id}",
                key='requests_ratelimits',
                value=json.dumps(self.requests_ratelimits)
            )
        return self.requests_ratelimits

    def _apply_rate_limit(self) -> Union[dict, None]:
        """
        Apply rate limits to the user ID and reset counters.

        Args:
            None

        Returns:
            (dict | None): Rate limit timestamp for the user ID, or None if not applicable.
            {
              "end_time": "2023-08-07 10:39:00.000000"
            }
                or
            None
        """
        # If the rate limit is already applied
        if self.requests_configuration['requests_per_day'] <= self.requests_counters['requests_per_day']:
            log.warning(
                '[class.%s] The request limits are exhausted (per_day), '
                'the rate limit will be applied for user ID %s',
                __class__.__name__,
                self.user_id
            )
            end_time = str(datetime.now() + timedelta(days=1))
            self.requests_ratelimits['end_time'] = end_time
            log.info(
                '[class.%s] Rate limit for user ID %s set to expire at %s',
                __class__.__name__,
                self.user_id,
                end_time
            )
        # If the rate limit is not yet applied
        elif self.requests_configuration['requests_per_hour'] <= self.requests_counters['requests_per_hour']:
            log.warning(
                '[class.%s] The request limits are exhausted (per_hour), '
                'the rate limit will be applied for user ID %s',
                __class__.__name__,
                self.user_id
            )
            shift_minutes = random.randint(1, self.requests_configuration['random_shift_minutes'])
            end_time = str(datetime.now() + timedelta(hours=1, minutes=shift_minutes))
            self.requests_ratelimits['end_time'] = end_time
            log.info(
                '[class.%s] Rate limit for user ID %s set to expire at %s',
                __class__.__name__,
                self.user_id,
                end_time
            )
        self.vault.write_secret(
            path=f"{self.vault_data_path}/{self.user_id}",
            key='requests_ratelimits',
            value=json.dumps(self.requests_ratelimits)
        )
        return self.requests_ratelimits

    def _update_requests_counters(self) -> None:
        """
        Update the request counters based on the historical user data.

        Args:
            None

        Returns:
            A dictionary containing the updated request counters.

        Examples:
            >>> ratelimits = RateLimits()
            >>> ratelimits._counters_watcher()
        """
        log.debug(
            '[class.%s] Calculating of request counters for user ID %s',
            __class__.__name__,
            self.user_id
        )
        requests_per_hour = 0
        requests_per_day = 0
        if self.requests_history:
            for request in self.requests_history:
                request_timestamp = datetime.strptime(request, '%Y-%m-%d %H:%M:%S.%f')
                if request_timestamp >= datetime.now() - timedelta(hours=1):
                    requests_per_hour = requests_per_hour + 1
                if request_timestamp >= datetime.now() - timedelta(days=1):
                    requests_per_day = requests_per_day + 1
        self.requests_counters = {
            'requests_per_hour': requests_per_hour,
            'requests_per_day': requests_per_day
        }
        self.vault.write_secret(
            path=f"{self.vault_data_path}/{self.user_id}",
            key='requests_counters',
            value=json.dumps(self.requests_counters)
        )
        log.info(
            '[class.%s] Current request counters: %s',
            __class__.__name__,
            self.requests_counters
        )
