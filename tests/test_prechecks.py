"""
A test that verifies the user __init__ function.
"""
import pytest


@pytest.mark.order(19)
def test_check_init_vault_conf(users_instance):
    """
    Checking the functionality of the init method of the class when the Vault configuration is passed
    """
    assert isinstance(users_instance.vault, object)
    print(users_instance.vault)
    assert users_instance.vault.kv2engine.read_secret(path='configuration/users/testUser1') is not None


@pytest.mark.order(20)
def test_check_init_postgres_data(users_instance):
    """
    Checking the functionality of the init method of the class when the Postgres test data is passed
    """
    assert isinstance(users_instance.vault, object)
    assert users_instance.storage.get_user_requests(user_id='testUser1') is not None
