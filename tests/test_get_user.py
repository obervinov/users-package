"""
A test that checks the function of the user's entry point.
"""
import re
import pytest


@pytest.mark.order(11)
def test_check_entrypoint_doesnt_exist_user(users):
    """
    Verify that the main entry point for user verification handles the case
    where the user does not exist.
    """
    user = 'testUser99'
    assert users.user_access_check(user_id=user) == {
                'access': 'denied'
    }


@pytest.mark.order(12)
def test_check_entrypoint_rl_disabled(users_without_rl):
    """
    Verify that the main entry point for user verification handles the case
    where rate limiting is disabled.
    """
    user = 'testUser9'
    assert users_without_rl.user_access_check(user_id=user, role_id='financial_role') == {
                'access': 'allowed',
                'permissions': 'allowed'
    }


@pytest.mark.order(13)
def test_check_entrypoint_authn_allowed(users):
    """
    Verify that the main entry point for user verification handles the case
    where authentication is allowed.
    """
    user = 'testUser2'
    assert users.user_access_check(user_id=user, role_id='financial_role') == {
                'access': 'allowed',
                'permissions': 'allowed',
                'rate_limits': {'end_time': None}
    }


@pytest.mark.order(14)
def test_check_entrypoint_authn_denied(users):
    """
    Verify that the main entry point for user verification handles the case
    where authentication is denied.
    """
    user = 'testUser4'
    assert users.user_access_check(user_id=user) == {
                'access': 'denied'
    }


@pytest.mark.order(15)
def test_check_entrypoint_authz_allowed(users):
    """
    Verify that the main entry point for user verification handles the case
    where authorization is allowed.
    """
    user = 'testUser2'
    assert users.user_access_check(user_id=user, role_id='financial_role') == {
                'access': 'allowed',
                'permissions': 'allowed',
                'rate_limits': {'end_time': None}
    }


@pytest.mark.order(16)
def test_check_entrypoint_authz_denied(users):
    """
    Verify that the main entry point for user verification handles the case
    where authorization is denied.
    """
    user = 'testUser2'
    assert users.user_access_check(user_id=user, role_id='admin_role') == {
                'access': 'allowed',
                'permissions': 'denied'
    }


@pytest.mark.order(17)
def test_check_entrypoint_rl_applied(users, timestamp_pattern):
    """
    Verify that the main entry point for user verification correctly applies rate limits
    and matches the end_time using a regular expression.
    """
    user = 'testUser5'
    result = users.user_access_check(user_id=user, role_id='financial_role')

    assert result['access'] == 'allowed'
    assert result['permissions'] == 'allowed'

    end_time = result['rate_limits']['end_time']
    assert re.match(timestamp_pattern, end_time) is not None


@pytest.mark.order(18)
def test_check_entrypoint_rl_not_applied(users):
    """
    Verify that the main entry point for user verification correctly handles the case
    where rate limits are not applied.
    """
    user = 'testUser2'
    assert users.user_access_check(user_id=user, role_id='financial_role') == {
                'access': 'allowed',
                'permissions': 'allowed',
                'rate_limits': {'end_time': None}
    }
