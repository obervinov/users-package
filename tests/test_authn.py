"""
A test that verifies the user authentication function.
"""
import pytest


@pytest.mark.order(1)
def test_check_authn_allow_user(users):
    """
    Check the function for the user who is allowed access to the bot
    """
    assert users.authentication(user_id='testUser1') == 'allowed'
    assert users.authentication(user_id='testUser2') == 'allowed'
    assert users.authentication(user_id='testUser3') == 'allowed'


@pytest.mark.order(2)
def test_check_authn_deny_user(users):
    """
    Check the function for the user who is forbidden access to the bot
    """
    assert users.authentication(user_id='testUser4') == 'denied'


@pytest.mark.order(3)
def test_check_authn_doesnt_exist_user(users):
    """
    Check the function for a user who does not exist in the configuration (random user)
    """
    assert users.authentication(user_id='testUser11') == 'denied'
    assert users.authentication(user_id='testUser12') == 'denied'
    assert users.authentication(user_id='123456789') == 'denied'
