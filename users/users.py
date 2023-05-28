"""
This module contains class and methods for implementing
the simplest authorization for telegram bots
"""
import datetime
from logger import log


class UsersAuth:
    """
    This class contains methods for performing the simplest authorization in telegram bots
    """

    def __init__(
        self,
        vault: object = None
    ) -> None:
        """
        A method for create a new Users Auth instance.

        Args:
            :param vault (object): vault instance for interacting with the vault api.

        Returns:
            None
        """
        self.vault = vault

    def check_permissions(
        self,
        userid: str = None
    ) -> str:
        """
        This method checks the rights of the user ID passed to it.

        Args:
            :param userid (str): user id of telegram account to check rights.

        Returns:
            (str) 'allow'
                or
            (str) 'deny'
        """
        try:
            permissions = self.vault.read_secret(
                path='configuration/permissions',
                key=str(userid)
            )
            if permissions == 'allow':
                log.info(
                    '[class.%s] access allowed from userid %s',
                    __class__.__name__,
                    userid
                )
                return self.record_event(
                    userid,
                    permissions
                )
        except KeyError:
            permissions = 'deny'
        log.error(
            '[class.%s] access denided from userid %s',
            __class__.__name__,
            userid
        )
        return self.record_event(
            userid,
            permissions
        )

    def record_event(
        self,
        userid,
        action
    ) -> str:
        """
        This method writes the login event by user id to the vault.

        Args:
            :param userid (int): user id of telegram account to check rights.
            :param action (str): response with permissions for the user ID.

        Returns:
            (str) 'allow'
                or
            (str) 'deny'
        """
        self.vault.write_secret(
            path='events/login',
            key=userid,
            value={
                'time': str(datetime.datetime.now()),
                'action': action
            }
        )
        return action
