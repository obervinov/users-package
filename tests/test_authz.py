"""
A test that checks the user authorization function.
"""
import pytest


@pytest.mark.order(4)
def test_check_authz_exist_role(users):
    """
    Check the function for the user who is allowed access to the exist role.
    """
    assert users.authorization(user_id='testUser1', role_id='admin_role') == 'allowed'
    assert users.authorization(user_id='testUser2', role_id='financial_role') == 'allowed'
    assert users.authorization(user_id='testUser2', role_id='goals_role') == 'allowed'


@pytest.mark.order(5)
def test_check_authz_doesnt_exist_role(users):
    """
    Check the function for the user who is denied access to the role.
    """
    assert users.authorization(user_id='testUser2', role_id='admin_role') == 'denied'
    assert users.authorization(user_id='testUser2', role_id='random_role') == 'denied'
    assert users.authorization(user_id='testUser2') == 'denied'
    assert users.authorization(user_id='testUser3', role_id='admin_role') == 'denied'
    assert users.authorization(user_id='testUser3', role_id='random_role') == 'denied'
    assert users.authorization(user_id='testUser3') == 'denied'
    assert users.authorization(user_id='testUser4', role_id='admin_role') == 'denied'
    assert users.authorization(user_id='testUser4', role_id='random_role') == 'denied'
    assert users.authorization(user_id='testUser4') == 'denied'
