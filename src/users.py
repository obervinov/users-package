######### THIS FILE FROM USERS AUTH BY BOT REQUESTS (whitelist/permissions) #########

### MODULES AND VARS ###
import datetime
from logger import log
### MODULES AND VARS ###


class UsersAuth:

    def __init__(self, vault, bot_name) -> None:
        self.vault = vault
        self.bot_name = bot_name

    def check_permission(self, chatid):
        telegram_allow = str(self.vault.vault_read_secrets(f"{self.bot_name}-config/config","whitelist"))
        vault_path_write = f"{self.bot_name}-login-events/" + str(chatid)

        log.info(f"[class.{__class__.__name__}] checking permissions from chat_id: {chatid}")

        if str(chatid) == telegram_allow:
            log.info(f"[class.{__class__.__name__}] access allowed from {chatid}")
            auth_state = "success"

        else: 
            log.warning(f"[class.{__class__.__name__}] access denided from chat_id: {chatid}")
            auth_state = "faild"

        self.vault.vault_put_secrets(vault_path_write, str(datetime.datetime.now()), auth_state)
        
        return auth_state