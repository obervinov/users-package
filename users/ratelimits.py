# pylint: disable=R0801
"""
This module provides the rate limit functionality for requests to the Telegram bot.
"""
import random
import math
from typing import Union
from datetime import datetime, timedelta
from logger import log
from vault import VaultClient
from .constants import VAULT_CONFIG_PATH, VAULT_DATA_PATH


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
        request_ratelimits (dict): Rate limit information for the user.

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
            self.request_ratelimits = {'end_time': None, 'first_request_time': None}

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
            'Before determining the rate limit status\n'
            'Counters: %s\n'
            'RateLimits: %s\n'
            'Config: %s\n',
            self.requests_counters,
            self.request_ratelimits,
            self.requests_configuration
        )

        # update the request counters based on the configured rate limits
        # and the time elapsed since the first response
        watcher = self.counters_watching()

        # If rate limits already applied
        if self.request_ratelimits['end_time']:
            rate_limits = self.active_rate_limit()

        # If rate limits need to apply
        elif (
            self.requests_configuration['requests_per_day'] <= self.requests_counters['requests_per_day'] or
            self.requests_configuration['requests_per_hour'] <= self.requests_counters['requests_per_hour']
        ):
            rate_limits = self.apply_rate_limit()

        # If no rate limits, just +1 to request counters
        elif (
            self.requests_configuration['requests_per_day'] > self.requests_counters['requests_per_day'] and
            self.requests_configuration['requests_per_hour'] > self.requests_counters['requests_per_hour']
        ):
            rate_limits = self.no_active_rate_limit()

        # If something went wrong
        else:
            rate_limits = None

        log.debug(
            'After determining the rate limit status\n'
            'Watcher: %s\n'
            'Counters: %s\n'
            'RateLimits: %s\n'
            'Config: %s\n',
            watcher,
            self.requests_counters,
            self.request_ratelimits,
            self.requests_configuration
        )

        return {
            'end_time': rate_limits['end_time'] if rate_limits else None
        }

    def active_rate_limit(self) -> Union[dict, None]:
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
        if self.request_ratelimits['end_time'] is None:
            return None

        if datetime.now() >= datetime.strptime(
            self.request_ratelimits['end_time'],
            '%Y-%m-%d %H:%M:%S.%f'
        ):
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
            self.vault.write_secret(
                path=f"{self.vault_data_path}/{self.user_id}",
                key='rate_limits',
                value=self.request_ratelimits
            )
        else:
            log.warning(
                '[class.%s] A speed limit has been detected for user ID %s '
                'that has already been applied and has not expired yet',
                __class__.__name__,
                self.user_id
            )
            # calculate the multiplier on the rate limit if requests continue to arrive after the application of rate_limit
            # in order to distribute the remaining requests in the same way based on the configuration
            restriction_multiplier_hours = math.ceil(
                self.requests_counters['requests_per_hour'] // self.requests_configuration['requests_per_hour']
            )
            first_timestamp = datetime.strptime(
                self.request_ratelimits['end_time'],
                '%Y-%m-%d %H:%M:%S.%f'
            )
            shift_minutes = random.randint(1, self.requests_configuration['random_shift_minutes'])

            self.request_ratelimits['end_time'] = str(
                first_timestamp + timedelta(
                    hours=restriction_multiplier_hours,
                    minutes=shift_minutes
                )
            )
            self.vault.write_secret(
                path=f"{self.vault_data_path}/{self.user_id}",
                key='rate_limits',
                value=self.request_ratelimits
            )

        return self.request_ratelimits

    def apply_rate_limit(self) -> Union[dict, None]:
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
        if self.requests_configuration['requests_per_day'] <= self.requests_counters['requests_per_day']:
            log.warning(
                '[class.%s] The request limits are exhausted (per_day), '
                'the rate limit will be applied for user ID %s',
                __class__.__name__,
                self.user_id
            )
            end_time = str(datetime.now() + timedelta(days=1))
            self.request_ratelimits['end_time'] = end_time
            self.requests_counters['requests_per_hour'] += 1
            self.requests_counters['requests_per_day'] += 1
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
            self.requests_counters['requests_per_day'] += 1
            self.requests_counters['requests_per_hour'] += 1
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
        Handles the case when the rate limit is not applied and you just need to increase the request counter.

        Args:
            None

        Returns:
            (dict): Always returns a dictionary with `None`
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

    def counters_watching(self) -> Union[dict, None]:
        """
        Update the request counters based on the configured rate limits and the time elapsed since the first request.

        Args:
            None

        Returns:
            A dictionary containing the updated request counters.

        Examples:
            >>> ratelimits = RateLimits()
            >>> ratelimits.counters_watching()
            {'per_hour': 10, 'per_day': 100, 'first_request_time': '2023-11-18 18:19:13.458355'}

        """
        log.info(
            '[class.%s] Updating request counters for user ID %s',
            __class__.__name__,
            self.user_id
        )

        if self.request_ratelimits.get('first_request_time', None) is None:
            self.request_ratelimits['first_request_time'] = str(datetime.now())

        else:
            shift_minutes = random.randint(1, self.requests_configuration['random_shift_minutes'])

            if (
                datetime.now() >= datetime.strptime(
                    self.request_ratelimits['first_request_time'],
                    '%Y-%m-%d %H:%M:%S.%f'
                ) + timedelta(hours=1, minutes=shift_minutes)
                and
                self.requests_counters['requests_per_hour'] != 0
            ):
                if (self.requests_counters['requests_per_hour'] - self.requests_configuration['requests_per_hour']) <= 0:
                    self.requests_counters['requests_per_hour'] = 0
                else:
                    self.requests_counters['requests_per_hour'] -= self.requests_configuration['requests_per_hour']

            if (
                datetime.now() >= datetime.strptime(
                    self.request_ratelimits['first_request_time'],
                    '%Y-%m-%d %H:%M:%S.%f'
                ) + timedelta(days=1)
                and
                self.requests_counters['requests_per_day'] != 0
            ):
                if (self.requests_counters['requests_per_day'] - self.requests_configuration['requests_per_day']) <= 0:
                    self.requests_counters['requests_per_day'] = 0
                else:
                    self.requests_counters['requests_per_day'] -= self.requests_configuration['requests_per_day']

            self.request_ratelimits['first_request_time'] = str(datetime.now())
            self.vault.write_secret(
                path=f"{self.vault_data_path}/{self.user_id}",
                key='request_ratelimits',
                value=self.request_ratelimits
            )

        response = {
            'per_hour': self.requests_counters['requests_per_hour'],
            'per_day': self.requests_counters['requests_per_day'],
            'first_request_time': self.request_ratelimits['first_request_time']
        }
        log.info(
            '[class.%s] Counters updated for user ID %s: %s',
            __class__.__name__,
            self.user_id,
            response
        )
        return response
