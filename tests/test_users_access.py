"""
A test that checks the function of the user's entry point.
"""
import re
import pytest
import datetime


@pytest.mark.order(1)
def test_users_doesnt_exist_user(users):
    """
    Verify behavior when the user does not exist in the Vault configuration (without rate limiting).
    """
    assert users.user_access_check(user_id='testUser99') == {'access': users.user_status_deny}


@pytest.mark.order(2)
def test_users_without_rl_doesnt_exist_user(users):
    """
    Verify behavior when the user does not exist in the Vault configuration (with rate limiting).
    """
    assert users.user_access_check(user_id='testUser99') == {'access': users.user_status_deny}


@pytest.mark.order(3)
def test_check_entrypoint_rl_disabled(users_without_rl):
    """
    Verify response when rate limiting is disabled.
    """
    assert users_without_rl.user_access_check(user_id='testUser1', role_id='admin_role') == {
                'access': users_without_rl.user_status_allow,
                'permissions': users_without_rl.user_status_allow
    }


@pytest.mark.order(4)
def test_check_entrypoint_rl_enabled(users, timestamp_pattern):
    """
    Verify response when rate limiting is enabled.
    """
    response = users.user_access_check(user_id='testUser1', role_id='admin_role')
    assert response['access'] == users.user_status_allow
    assert response['permissions'] == users.user_status_allow
    assert re.match(timestamp_pattern, str(response['rate_limits'])) is not None
    assert isinstance(response['rate_limits'], datetime.datetime)


### TEST CASES FOR EXIST AND DOESNT EXIST ROLES ###







def test_check_entrypoint_authn_allowed(users):
    """
    Verify that the main entry point for user verification handles the case
    where authentication is allowed.
    """
    user = 'testUser2'
    assert users.user_access_check(user_id=user, role_id='financial_role') == {
                'access': users.user_status_allow,
                'permissions': users.user_status_allow,
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
                'access': users.user_status_deny
    }


@pytest.mark.order(15)
def test_check_entrypoint_authz_allowed(users):
    """
    Verify that the main entry point for user verification handles the case
    where authorization is allowed.
    """
    user = 'testUser2'
    assert users.user_access_check(user_id=user, role_id='financial_role') == {
                'access': users.user_status_allow,
                'permissions': users.user_status_allow,
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
                'access': users.user_status_allow,
                'permissions': users.user_status_deny
    }


@pytest.mark.order(17)
def test_check_entrypoint_rl_applied(users, timestamp_pattern):
    """
    Verify that the main entry point for user verification correctly applies rate limits
    and matches the end_time using a regular expression.
    """
    user = 'testUser5'
    result = users.user_access_check(user_id=user, role_id='financial_role')

    assert result['access'] == users.user_status_allow
    assert result['permissions'] == users.user_status_allow

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
                'access': users.user_status_allow,
                'permissions': users.user_status_allow,
                'rate_limits': {'end_time': None}
    }
