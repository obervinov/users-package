"""
A test that verifies the user __init__ function.
"""
import pytest
# pylint: disable=E0611
from users import Users


@pytest.mark.order(19)
def test_check_init_vault_conf(vault_configuration):
    """
    Checking the functionality of the init method of the class when the vault configuration is passed
    """
    users = Users(vault=vault_configuration)
    assert isinstance(
        users.vault,
        object
    )
    print(users.vault)
    assert users.vault.read_secret(
        path='data/users/testUser1'
    ) is not None


@pytest.mark.order(20)
def test_check_init_vault_instance(vault_instance):
    """
    Checking the functionality of the init method of the class when the vault instance is passed
    """
    users = Users(vault=vault_instance)
    assert isinstance(
        users.vault,
        object
    )
    assert users.vault.read_secret(
        path='data/users/testUser1'
    ) is not None
