"""
This module contains classes and functions for implementing
the simplest authorization for telegram bots
"""
import datetime
from logger import log


class UsersAuth:
    """
    This class contains functions for performing the simplest authorization in telegram bots
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
        This method checks the chat ID passed to it for the presence in the vault whitelist.
        After verification, it blocks by writing to the vault.
        
        :param userid: User id of telegram account to check rights on whitelist.
        :type userid: int
        :default userid: None
        """
        permissions = self.vault_client.vault_read_secrets(
            'configuration/premissions',
            userid
        )
        log.info(
            '[class.%s] checking permissions from user id %s',
            __class__.__name__,
            userid
        )
        if permissions == 'allow':
            log.info(
                '[class.%s] access allowed from user id %s',
                __class__.__name__,
                userid
            )
            self.vault_client.vault_put_secrets(
                'events/login',
                userid,
                {
                    'time': datetime.datetime.now(),
                    'action': 'allow'
                }
            )
            return 'allow'
        log.error(
            '[class.%s] access denided from user id %s',
            __class__.__name__,
            userid
        )
        self.vault_client.vault_put_secrets(
            'events/login',
            userid,
            {
                'time': datetime.datetime.now(),
                'action': 'deny'
            }
        )
        return 'deny'
