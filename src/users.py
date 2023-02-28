"""This module contains classes and functions for implementing
the simplest authorization for telegram bots"""
import datetime
from logger import log


class UsersAuth:
    """This class contains functions for performing the simplest authorization in telegram bots
    """

    def __init__(self, vault: object = None, bot_name: str = None) -> None:
        """A function for create a new UserAuth client instance.
        :param vault: Vault object for interacting with the vault api.
        :type vault: object
        :default vault: None
        :param bot_name: The name of the bot, for setting up paths to configurations in the vault.
        :type bot_name: str
        :default bot_name: None
        """
        self.vault = vault
        self.bot_name = bot_name


    def check_permission(self, chatid: int = None) -> str:
        """This function checks the chat ID passed to it for the presence in the vault whitelist.
        After verification, it blocks by writing to the vault.
        :param chatid: Chat id of telegram account to check rights on whitelist.
        :type chatid: int
        :default chatid: None
        """
        telegram_allow = self.vault.vault_read_secrets(
            f"{self.bot_name}-config/config","whitelist"
        )
        vault_path_write = f"{self.bot_name}-login-events/" + str(chatid)

        log.info(f"[class.{__class__.__name__}] checking permissions from chat_id: {chatid}")

        if str(chatid) == telegram_allow:
            log.info(f"[class.{__class__.__name__}] access allowed from {chatid}")
            self.vault.vault_put_secrets(
                vault_path_write, str(datetime.datetime.now()),
                "success"
            )
            return "success"
        if str(chatid) != telegram_allow:
            log.warning(f"[class.{__class__.__name__}] access denided from chat_id: {chatid}")
            self.vault.vault_put_secrets(vault_path_write, str(datetime.datetime.now()), "faild")
            return "faild"
        return None
