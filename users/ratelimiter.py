# pylint: disable=R0801
"""
This module provides the rate limit functionality for requests to the Telegram bot.
"""
import random
import json
from json.decoder import JSONDecodeError
from datetime import datetime, timedelta
from logger import log
from vault import VaultClient
from .constants import USERS_VAULT_CONFIG_PATH
from .storage import Storage
from .exceptions import WrongUserConfiguration, VaultInstanceNotSet, FailedDeterminateRateLimit, StorageInstanceNotSet


# pylint: disable=too-many-instance-attributes
class RateLimiter:
    """
    The RateLimiter class provides the rate limit functionality for requests
    to the Telegram bot in the context of a specific user.

    Attributes:
        vault (VaultClient): VaultClient instance for interacting with the Vault API.
        storage (Storage): Storage instance for storing user data.
        vault_config_path (str): Path to the configuration data in Vault.
        user_id (str): User ID for checking rate limits.
        requests_configuration (dict): The user requests configuration.
        requests_counters (dict): The user request counters.
        user_requests (list): The user requests list.

    Methods:
        determine_rate_limit: Determine the rate limit status for the user ID.
        _validate_rate_limit: Check and handle active rate limits for the user ID.
        _apply_rate_limit: Apply rate limits to the user ID and return the rate limit timestamp.
        get_user_request_counters: Calculate the user request counters: per hour and per day.

    Raises:
        VaultInstanceNotSet: If the Vault instance is not set.
        WrongUserConfiguration: If the user configuration in Vault is wrong.
        FailedDeterminateRateLimit: If the rate limit for the user ID cannot be determined.
    """
    def __init__(
        self,
        vault: VaultClient = None,
        storage: Storage = None,
        user_id: str = None
    ) -> None:
        """
        Create a new RateLimiter instance.

        Args:
            :param vault (VaultClient): VaultClient instance for interacting with the Vault API.
            :param storage (Storage): Storage instance for storing user data.
            :param user_id (str): User ID for checking rate limits.

        Examples:
            >>> limiter = RateLimiter(vault=vault_client, storage=storage_client, user_id='user_id')
        """
        # Extract the Vault instance
        if isinstance(vault, VaultClient):
            self.vault = vault
        else:
            log.error('[Users.RateLimiter]: wrong vault parameters in Users(vault=%s), see doc-string', vault)
            raise VaultInstanceNotSet("Vault instance is not set. Please provide a valid Vault instance as instance.")

        # Extract the Storage instance
        if isinstance(storage, Storage):
            self.storage = storage
        else:
            log.error('[Users.RateLimiter]: wrong storage parameters in Users(storage=%s), see doc-string', storage)
            raise StorageInstanceNotSet("Storage instance is not set. Please provide a valid Storage instance as instance.")

        # Extract required parameters
        self.user_id = user_id
        self._vault_config_path = USERS_VAULT_CONFIG_PATH

        # Read general user configuration from Vault and extract requests configuration
        user_configuration = self.vault.kv2engine.read_secret(path=f"{self.vault_config_path}/{self.user_id}")
        requests_configuration = user_configuration.get('requests', None)
        if requests_configuration:
            try:
                self.requests_configuration = json.loads(requests_configuration)
            except (TypeError, JSONDecodeError) as error:
                log.error('[Users.RateLimiter]: Wrong value for requests configuration for user ID %s: %s', self.user_id, error)
                raise WrongUserConfiguration("User configuration in Vault is wrong. Please provide a valid configuration for requests.") from error
        else:
            log.error('[Users.RateLimiter]: No requests configuration found for user ID %s', self.user_id)
            raise WrongUserConfiguration("User configuration in Vault is wrong. Please provide a valid configuration for rate limits.")

        self.user_requests = self.storage.get_user_requests(user_id=user_id)
        self.requests_counters = self.get_user_request_counters()

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

    def determine_rate_limit(self) -> datetime | None:
        """
        Determine the rate limit status for the user ID.

        Returns:
            (datetime | None): Rate limit timestamp for the user ID.
            2023-08-07 10:39:00.000000
                or
            None

        Examples:
            >>> rl_status = limiter.determine_rate_limit()
        """
        rate_limits = None

        # Get the rate limits for the user ID
        user_requests = self.storage.get_user_requests(user_id=self.user_id, order="rate_limits DESC")
        if user_requests:
            # If rate limits is active (compared the last request with the current time)
            exist_rate_limit = user_requests[0][2]
            if exist_rate_limit and datetime.strptime(exist_rate_limit, '%Y-%m-%d %H:%M:%S.%f') >= datetime.now():
                rate_limits = self._validate_rate_limit()
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
                rate_limits = None
            # If something went wrong
            else:
                log.error(
                    '[Users.RateLimiter]: Failed to determinate rate limit for user ID %s:\nConfiguration: %s\nCounters: %s',
                    self.user_id, self.requests_configuration, self.requests_counters
                )
                raise FailedDeterminateRateLimit("Failed to determinate rate limit for the user ID.")
        return rate_limits

    def _validate_rate_limit(self) -> datetime | None:
        """
        Check and handle active rate limits for the user ID.

        Returns:
            (datetime | None): Rate limit timestamp for the user ID or None if the time has already expired.
            2023-08-07 10:39:00.000000
                or
            None
        """
        latest_rate_limit_timestamp = self.storage.get_user_requests(user_id=self.user_id, order="rate_limits DESC", limit=1)[0][2]
        per_day_exceeded = self.requests_counters['requests_per_day'] >= self.requests_configuration['requests_per_day']
        per_hour_exceeded = self.requests_counters['requests_per_hour'] >= self.requests_configuration['requests_per_hour']

        # If the rate limit has already expired - reset the rate limit
        if datetime.now() >= datetime.strptime(latest_rate_limit_timestamp, '%Y-%m-%d %H:%M:%S.%f'):
            log.info('[Users.RateLimiter]: The rate limit %s for user ID %s has expired and will be reset', latest_rate_limit_timestamp, self.user_id)
            return None

        if per_day_exceeded or per_hour_exceeded:
            new_rate_limit = None
            # Case1: If the counter exceeds the configuration per DAY
            if per_day_exceeded:
                if latest_rate_limit_timestamp:
                    new_rate_limit = datetime.strptime(latest_rate_limit_timestamp, '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=1)
                else:
                    new_rate_limit = datetime.now() + timedelta(days=1)

            # Case2: If the counter exceeds the configuration per HOUR
            elif per_hour_exceeded:
                shift_minutes = random.randint(1, self.requests_configuration['random_shift_minutes'])
                if latest_rate_limit_timestamp:
                    new_rate_limit = datetime.strptime(latest_rate_limit_timestamp, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=1, minutes=shift_minutes)
                else:
                    new_rate_limit = datetime.now() + timedelta(hours=1, minutes=shift_minutes)

            log.info('[Users.RateLimiter]: The rate limit already applied for user ID %s. Rate limit: %s', self.user_id, str(new_rate_limit))
            return new_rate_limit

        log.error(
            '[Users.RateLimiter]: Failed to validate rate limit for user ID %s:\nConfiguration: %s\nCounters: %s',
            self.user_id, self.requests_configuration, self.requests_counters
        )
        raise FailedDeterminateRateLimit("Failed to determinate rate limit for the user ID.")

    def _apply_rate_limit(self) -> datetime | None:
        """
        Apply rate limits to the user ID and return the rate limit timestamp.

        Returns:
            (datetime | None): Rate limit timestamp for the user ID, or None if not applicable.
            2023-08-07 10:39:00.000000
                or
            None
        """
        result = self.storage.get_user_requests(user_id=self.user_id, order="rate_limits DESC", limit=1)

        # If the rate limit is already applied
        if self.requests_configuration['requests_per_day'] <= self.requests_counters['requests_per_day']:
            if result and result[0][2] is not None:
                latest_rate_limit_timestamp = result[0][2]
                rate_limit = datetime.strptime(latest_rate_limit_timestamp, '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=1)
            else:
                rate_limit = datetime.now() + timedelta(days=1)
            log.info('[Users.RateLimiter]: The requests limit per day are exhausted for user ID %s. The rate limit will expire at %s', self.user_id, str(rate_limit))
        # If the rate limit is not yet applied
        elif self.requests_configuration['requests_per_hour'] <= self.requests_counters['requests_per_hour']:
            shift_minutes = random.randint(1, self.requests_configuration['random_shift_minutes'])
            rate_limit = datetime.now() + timedelta(hours=1, minutes=shift_minutes)
            log.info('[Users.RateLimiter]: The requests limit per hour are exhausted for user ID %s. The rate limit will expire at %s', self.user_id, str(rate_limit))

        return rate_limit

    def get_user_request_counters(self) -> dict:
        """
        Calculate the user request counters: per hour and per day.

        Returns:
            (dict): The user request counters.
            {'requests_per_hour': 0, 'requests_per_day': 0}

        Examples:
            >>> ratelimits = RateLimits()
            >>> ratelimits.get_user_request_counters()
        """
        requests_per_hour = 0
        requests_per_day = 0
        if self.user_requests:
            for request in self.user_requests:
                request_timestamp = request[1]
                if request_timestamp >= datetime.now() - timedelta(hours=1):
                    requests_per_hour = requests_per_hour + 1
                if request_timestamp >= datetime.now() - timedelta(days=1):
                    requests_per_day = requests_per_day + 1
        log.debug(
            '[Users.RateLimiter]: User ID %s: Counters %s, Requests %s',
            self.user_id, self.user_requests, {'requests_per_hour': requests_per_hour, 'requests_per_day': requests_per_day}
        )
        return {
            'requests_per_hour': requests_per_hour,
            'requests_per_day': requests_per_day
        }
