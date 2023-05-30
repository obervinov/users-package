"""
This test is necessary to verify permissions on the provided user ID.
"""
import pytest


@pytest.mark.order(1)
def test_check_permissions_allow(userauth):
    """
    Test to check the allow of permissions for the user ID
    """
    assert userauth.check_permissions(123456) == 'allow'


@pytest.mark.order(2)
def test_check_permissions_deny(userauth):
    """
    Test to check the deny of permissions for the user ID
    """
    assert userauth.check_permissions(654321) == 'deny'


@pytest.mark.order(3)
def test_check_permissions_not_exist(userauth):
    """
    Test to check when the user id does not exist in the vault
    """
    assert userauth.check_permissions(111111) == 'deny'
