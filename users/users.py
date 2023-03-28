"""
This module contains classes and methods for implementing
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
        vault_client: object = None
    ) -> None:
        """
        A method for create a new UserAuth client instance.
        
        :param vault_client: Vault object for interacting with the vault api.
        :type vault_client: object
        :default vault_client: None
        """
        self.vault_client = vault_client


    def check_permissions(
        self,
        userid: int = None
    ) -> str:
        """
        This method checks the rights of the user ID passed to it.
        
        :param userid: User id of telegram account to check rights.
        :type userid: int
        :default userid: None
        return: 'allow' or 'deny'
        """
        permission = self.vault_client.vault_read_secrets(
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
        
        :param userid: User id of telegram account to check rights.
        :type userid: int
        :default userid: None
        :param action: Response from the check_permissions() with permissions for the user ID.
        :type action: str
        :default action: None
        """
        self.vault_client.vault_put_secrets(
            'events/login',
            userid,
            {
                'time': datetime.datetime.now(),
                'action': action
            }
        )
