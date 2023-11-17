"""
A test that verifies the user authentication function.
"""
import pytest


@pytest.mark.order(1)
def test_check_authn_allow_users(users):
    """
    Check the function for the user who is allow access to the bot
    """
    assert users.authentication(user_id='testUser1') == users.user_status_allow
    assert users.authentication(user_id='testUser2') == users.user_status_allow
    assert users.authentication(user_id='testUser3') == users.user_status_allow


@pytest.mark.order(2)
def test_check_authn_deny_users(users):
    """
    Check the function for the user who is forbidden access to the bot
    """
    assert users.authentication(user_id='testUser4') == users.user_status_deny


@pytest.mark.order(3)
def test_check_authn_doesnt_exist_users(users):
    """
    Check the function for a user who does not exist in the configuration (random user)
    """
    assert users.authentication(user_id='testUser91') == users.user_status_deny
    assert users.authentication(user_id='testUser91') == users.user_status_deny
    assert users.authentication(user_id='123456789') == users.user_status_deny
