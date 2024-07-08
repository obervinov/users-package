"""
A test that checks the function of the user's entry point.
"""
import re
import datetime
import pytest


@pytest.mark.order(1)
def test_users_doesnt_exist_user(users):
    """
    Verify behavior when the user does not exist in the Vault configuration (without rate limiting).
    """
    user_info = users.user_access_check(user_id='testUser99')
    user_info_with_role = users.user_access_check(user_id='testUser99', role_id='admin_role') 
    assert user_info['access'] == users.user_status_deny
    assert user_info.get('permissions', None) is None
    assert user_info_with_role['access'] == users.user_status_deny
    assert user_info_with_role.get('permissions', None) is None


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


@pytest.mark.order(5)
def test_authorization_exist_roles(users):
    """
    Verify response when the user has the role.
    """
    assert users.user_access_check(user_id='testUser1', role_id='admin_role')['permissions'] == users.user_status_allow
    assert users.user_access_check(user_id='testUser2', role_id='financial_role')['permissions'] == users.user_status_allow
    assert users.user_access_check(user_id='testUser2', role_id='goals_role')['permissions'] == users.user_status_allow


@pytest.mark.order(5)
def test_authorization_doesnt_exist_roles(users):
    """
    Verify response when the user does not have the role.
    """
    assert users.user_access_check(user_id='testUser2', role_id='admin_role')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser2', role_id='guest_role')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser2')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser3', role_id='admin_role')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser3', role_id='guest_role')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser3')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser4', role_id='admin_role')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser4', role_id='guest_role')['permissions'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser4')['permissions'] == users.user_status_deny


@pytest.mark.order(6)
def test_authentication_user_denied(users):
    """
    Verify response when the user is denied access.
    """
    assert users.user_access_check(user_id='testUser20')['access'] == users.user_status_deny
    assert users.user_access_check(user_id='testUser20', role_id='admin_role')['access'] == users.user_status_deny


@pytest.mark.order(7)
def test_authorization_user_denied(users):
    """
    Verify response when the user is denied access.
    """
    assert users.user_access_check(user_id='testUser21')['access'] == users.user_status_allowed
    assert users.user_access_check(user_id='testUser21')['permissions'] == users.user_status_allowed
    assert users.user_access_check(user_id='testUser21', role_id='admin_role')['permissions'] == users.user_status_deny
