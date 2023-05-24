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
        userid: int = None
    ) -> str:
        """
        This method checks the rights of the user ID passed to it.

        Args:
            :param userid (int): user id of telegram account to check rights.

        Returns:
            (str) 'allow'
                or
            (str) 'deny'
        """
        permission = self.vault.vault_read_secrets(
            'configuration/permissions',
            userid
        )
        log.info(
            '[class.%s] checking permissions from user id %s',
            __class__.__name__,
            userid
        )
        if permission == 'allow':
            log.info(
                '[class.%s] access allowed from user id %s',
                __class__.__name__,
                userid
            )
            self.record_event(
                userid,
                permission
            )
            return permission
        log.error(
            '[class.%s] access denided from user id %s',
            __class__.__name__,
            userid
        )
        self.record_event(
            userid,
            permission
        )
        return permission

    def record_event(
        self,
        userid,
        action
    ) -> None:
        """
        This method writes the login event by user id to the vault.

        Args:
            :param userid (int): user id of telegram account to check rights.
            :param action (str): response with permissions for the user ID.

        Returns:
            None
        """
        self.vault.vault_put_secrets(
            'events/login',
            userid,
            {
                'time': datetime.datetime.now(),
                'action': action
            }
        )
