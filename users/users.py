"""
This module contains classes and methods for implementing
the simplest authorization and management of user attributes in Telegram bots.
"""
import random
from datetime import datetime, timedelta
from logger import log


class Users:
    """
    This module contains classes and methods for implementing the simplest
    authentication, authorization, limiting the speed of requests,
    and managing user attributes in Telegram bots.
    """

    def __init__(
        self,
        vault: object = None,
        rate_limits: bool = True
    ) -> None:
        """
        Method to create a new Users instance.

        Args:
            :param vault (object): Vault instance for interacting with the Vault API.
            :param rate_limits (bool): Enable rate limit functionality.

        Returns:
            None

        Examples:
            >>> users_without_ratelimits = Users(
                    vault=vault_client,
                    rate_limits=False
                )
            >>> users_with_ratelimits = Users(
                    vault=vault_client
                )
        """
        self.vault = vault
        self.rate_limits = rate_limits

    def user_access_check(
        self,
        user_id: str = None,
        role_id: str = None
    ) -> dict:
        """
        The main entry point for authentication, authorization, and verification of the rate limit.

        Args:
            :param user_id (str): Required user ID.
            :param role_id (str): Required role ID for the specified user ID.

        Returns:
            (dict) {
                'access': 'allowed'/'denied'
            }
              or
            (dict) {
                'access': 'allowed'/'denied',
                'permissions': 'allowed'/'denied'
            }
              or
            (dict) {
                'access': 'allowed'/'denied',
                'permissions': 'allowed'/'denied',
                'rate_limits': {
                    'end_time': '2023-08-06 11:47:09.440933'
                }
            }
              or
            (dict) {
                'access': 'allowed'/'denied',
                'permissions': 'allowed'/'denied',
                'rate_limits': {
                    'end_time': None,
                }
            }

        Examples:
            >>> user_info = users.user_access_check(
                user_id='user1',
                role_id='admin_role'
            )
        """
        user_info = {}

        user_info['access'] = self.authentication(
            user_id=user_id
        )
        if user_info['access'] == 'allowed' and role_id:
            user_info['permissions'] = self.authorization(
                user_id=user_id,
                role_id=role_id
            )
            if user_info['permissions'] == 'allowed' and self.rate_limits:
                user_info['rate_limits'] = self.rl_controller(
                    user_id=user_id
                )

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
            (str) 'allowed'
                or
            (str) 'denied'
        """
        try:
            status = self.vault.read_secret(
                path=f"configuration/users/{user_id}",
                key='status'
            )
        # pylint: disable=W0718
        # Fixed after https://github.com/obervinov/vault-package/issues/31
        except Exception:
            status = 'denied'

        log.info(
            '[class.%s] Access from user ID %s: %s',
            __class__.__name__,
            user_id,
            status
        )
        self.vault.write_secret(
            path=f"data/users/{user_id}",
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
            (str) 'allowed'
                or
            (str) 'denied'
        """
        try:
            if role_id in self.vault.read_secret(
                path=f"configuration/users/{user_id}",
                key='roles'
            ):
                status = 'allowed'
            else:
                status = 'denied'
        # pylint: disable=W0718
        # Fixed after https://github.com/obervinov/vault-package/issues/31
        except Exception:
            status = 'denied'

        log.info(
            '[class.%s] User ID %s has the role %s: %s',
            __class__.__name__,
            user_id,
            role_id,
            status
        )
        self.vault.write_secret(
            path=f"data/users/{user_id}",
            key='authorization',
            value={
                'time': str(datetime.now()),
                'status': status,
                'role': role_id
            }
        )
        return status

    def rl_controller(
        self,
        user_id: str = None,
        consider_request: bool = True
    ) -> dict:
        """
        The method takes into account user requests and, depending on the counter,
        applies or does not apply rate limits.

        Args:
            :param user_id (str): Required user ID.
            :param consider_request (bool): Specifies whether the method should include
                                            the current request in the request counters.

        Examples:
          >>> rl_controller(
                user_id='user1'
              )
          >>> rl_controller(
                user_id='user1',
                consider_request=False
              )

        Returns:
            (dict) {'end_time': None}
                or
            (dict) {'end_time': '2023-08-06 11:47:09.440933'}
        """
        if not consider_request:
            log.warning(
                '[class.%s] Consider request disabled',
                __class__.__name__,
            )

        # Read configuration and history counters
        requests_configuration = self.vault.read_secret(
            path=f"configuration/users/{user_id}",
            key='requests'
        )
        try:
            requests_counters = self.vault.read_secret(
                path=f"data/users/{user_id}",
                key='requests_counters'
            )
        # pylint: disable=W0718
        # Fixed after https://github.com/obervinov/vault-package/issues/31
        except Exception:
            requests_counters = {'requests_per_day': 0, 'requests_per_hour': 0}

        try:
            requests_ratelimits = self.vault.read_secret(
                path=f"data/users/{user_id}",
                key='rate_limits'
            )
        # pylint: disable=W0718
        # Fixed after https://github.com/obervinov/vault-package/issues/31
        except Exception:
            requests_ratelimits = {'end_time': None}

        # Determine the status of the request limit
        # If rate limits already applied
        if requests_ratelimits['end_time']:
            if datetime.now() >= datetime.strptime(
                requests_ratelimits['end_time'], '%Y-%m-%d %H:%M:%S.%f'
            ):
                log.info(
                    '[class.%s] Date rate limit expired, reset for user ID %s',
                    __class__.__name__,
                    user_id
                )
                requests_ratelimits['end_time'] = None
                self.vault.write_secret(
                    path=f"data/users/{user_id}",
                    key='rate_limits',
                    value={
                        'end_time': requests_ratelimits['end_time']
                    }
                )
            else:
                log.warning(
                    '[class.%s] A speed limit has been detected for user ID %s '
                    'that has already been applied and has not expired yet',
                    __class__.__name__,
                    user_id
                )
            rate_limits = requests_ratelimits

        # If rate limits need to apply
        elif (
            requests_configuration['requests_per_day'] <= requests_counters['requests_per_day'] or
            requests_configuration['requests_per_hour'] <= requests_counters['requests_per_hour']
        ):
            if requests_configuration['requests_per_day'] <= requests_counters['requests_per_day']:
                log.warning(
                    '[class.%s] The request limits are exhausted (per_day), '
                    'the rate limit will be applied for user ID %s',
                    __class__.__name__,
                    user_id
                )
                requests_ratelimits['end_time'] = str(datetime.now() + timedelta(days=1))
                requests_counters['requests_per_day'] = 0
                requests_counters['requests_per_hour'] = requests_counters['requests_per_hour'] + 1
            elif requests_configuration['requests_per_hour'] <= requests_counters['requests_per_hour']:
                log.warning(
                    '[class.%s] The request limits are exhausted (per_hour), '
                    'the rate limit will be applied for user ID %s',
                    __class__.__name__,
                    user_id
                )
                shift_minutes = random.randint(1, requests_configuration['random_shift_minutes'])
                requests_ratelimits['end_time'] = str(
                    datetime.now() + timedelta(
                        hours=1,
                        minutes=shift_minutes
                    )
                )
                requests_counters['requests_per_hour'] = 0
                requests_counters['requests_per_day'] = requests_counters['requests_per_day'] + 1
            self.vault.write_secret(
                path=f"data/users/{user_id}",
                key='requests_counters',
                value=requests_counters
            )
            self.vault.write_secret(
                path=f"data/users/{user_id}",
                key='rate_limits',
                value=requests_ratelimits
            )
            rate_limits = requests_ratelimits

        # If no rate limits need to be applied
        elif (
            requests_configuration['requests_per_day'] > requests_counters['requests_per_day'] and
            requests_configuration['requests_per_hour'] > requests_counters['requests_per_hour'] and
            consider_request
        ):
            log.info(
                '[class.%s] The limits have not been exhausted, '
                'the limits on the number of requests are not applied for user ID %s',
                __class__.__name__,
                user_id
            )
            requests_counters['requests_per_day'] = requests_counters['requests_per_day'] + 1
            requests_counters['requests_per_hour'] = requests_counters['requests_per_hour'] + 1
            self.vault.write_secret(
                path=f"data/users/{user_id}",
                key='requests_counters',
                value=requests_counters
            )
            rate_limits = {'end_time': None}
        else:
            log.error(
                '[class.%s] Failed to apply rate limit for %s\n'
                'Counters: %s \n'
                'Ratelimits: %s \n'
                'Configuration: %s',
                __class__.__name__,
                user_id,
                requests_counters,
                requests_ratelimits,
                requests_configuration
            )
            rate_limits = None

        return rate_limits
