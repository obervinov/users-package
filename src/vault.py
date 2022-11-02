######### THIS FUNCTIONS VAULT CLIENT FROM READ/WRITE SECRETS #########

### MODULES AND VARS ###
import hvac
from logger import log
### MODULES AND VARS ###

class VaultClient:

    def __init__(self, vault_addr, vault_approle_id, vault_approle_secret_id, vault_mount_point) -> None:
        self.vault_addr = vault_addr
        self.vault_approle_id = vault_approle_id
        self.vault_approle_secret_id = vault_approle_secret_id
        self.vault_mount_point = vault_mount_point

        # vault approle https://www.vaultproject.io/api-docs/auth/approle
        vault_object = hvac.Client(url=self.vault_addr,)

        try:          
          vault_approle_auth = vault_object.auth.approle.login(role_id=self.vault_approle_id, secret_id=self.vault_approle_secret_id)['auth']
          vault_object.secrets.kv.v2.configure(max_versions=5000, mount_point=self.vault_mount_point, cas_required=False,)
          
          log.info(f"[class.{__class__.__name__}] kv engine is configured, token id {vault_approle_auth['entity_id']}")  
          self.vault_object = vault_object

        except Exception as ex:
          log.error(f"[class.{__class__.__name__}] exception init kv engine: {ex}")


    def vault_read_secrets(self, path, secret_key=None):
        try:
          read_response = self.vault_object.secrets.kv.v2.read_secret_version(path=path,mount_point=self.vault_mount_point,)
          
          if secret_key == None:
            response = read_response['data']['data']
          else:
            response = read_response['data']['data'][secret_key]

        except hvac.exceptions.InvalidPath:
          read_response = {'data': {'data': {'exception': 'InvalidPath'}}}
          response = read_response['data']['data']

        except Exception as ex:
            log.warn(f"[class.{__class__.__name__}] exception getting secret {self.vault_mount_point}/{path}/{secret_key}: {ex}")
        
        return response


    def vault_put_secrets(self, path, key, value):
        key_value = {}
        key_value[key]=value

        try:
            self.vault_object.secrets.kv.v2.create_or_update_secret(path=path, cas=0, secret=key_value, mount_point=self.vault_mount_point,)

        except hvac.exceptions.InvalidRequest:
            self.vault_patch_secrets(path, key_value) 

        except Exception as ex:
            log.error(f"[class.{__class__.__name__}] exception in secret {path}: {ex}")


    def vault_patch_secrets(self, path, key_value):
        try:
            self.vault_object.secrets.kv.v2.patch(path=path, secret=key_value, mount_point=self.vault_mount_point, )

        except Exception as ex:
            log.error(f"[class.{__class__.__name__}] exception in secret {path}: {ex}")


    def vault_list_secrets(self, path):
        try:
            response = self.vault_object.secrets.kv.v2.list_secrets(path=path, mount_point=self.vault_mount_point)['data']['keys']
            return response
        except Exception as ex:
            log.error(f"[class.{__class__.__name__}] exception list secret {path}: {ex}")