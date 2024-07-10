"""
A test that checks the function of the user's entry point.
"""
import re
import datetime
import pytest


@pytest.mark.order(1)
def test_users_doesnt_exist_user(users_instance):
    """
    Verify behavior when the user does not exist in the Vault configuration (without rate limiting).
    """
    user_info = users_instance.user_access_check(user_id='testUser99')
    user_info_with_role = users_instance.user_access_check(user_id='testUser99', role_id='admin_role') 
    assert user_info['access'] == users_instance.user_status_deny
    assert user_info.get('permissions', None) is None
    assert user_info_with_role['access'] == users_instance.user_status_deny
    assert user_info_with_role.get('permissions', None) is None


@pytest.mark.order(2)
def test_users_without_rl_doesnt_exist_user(users_instance):
    """
    Verify behavior when the user does not exist in the Vault configuration (with rate limiting).
    """
    assert users_instance.user_access_check(user_id='testUser99') == {'access': users_instance.user_status_deny}


@pytest.mark.order(3)
def test_check_entrypoint_rl_disabled(users_instance_without_rl):
    """
    Verify response when rate limiting is disabled.
    """
    assert users_instance_without_rl.user_access_check(user_id='testUser1', role_id='admin_role') == {
                'access': users_instance_without_rl.user_status_allow,
                'permissions': users_instance_without_rl.user_status_allow
    }


@pytest.mark.order(4)
def test_check_entrypoint_rl_enabled(users_instance, timestamp_pattern):
    """
    Verify response when rate limiting is enabled.
    """
    response = users_instance.user_access_check(user_id='testUser1', role_id='admin_role')
    assert response['access'] == users_instance.user_status_allow
    assert response['permissions'] == users_instance.user_status_allow
    assert re.match(timestamp_pattern, str(response['rate_limits'])) is not None
    assert isinstance(response['rate_limits'], datetime.datetime)


@pytest.mark.order(5)
def test_authorization_exist_roles(users_instance):
    """
    Verify response when the user has the role.
    """
    assert users_instance.user_access_check(user_id='testUser1', role_id='admin_role')['permissions'] == users_instance.user_status_allow
    assert users_instance.user_access_check(user_id='testUser2', role_id='financial_role')['permissions'] == users_instance.user_status_allow
    assert users_instance.user_access_check(user_id='testUser2', role_id='goals_role')['permissions'] == users_instance.user_status_allow


@pytest.mark.order(5)
def test_authorization_doesnt_exist_roles(users_instance):
    """
    Verify response when the user does not have the role.
    """
    assert users_instance.user_access_check(user_id='testUser2', role_id='admin_role')['permissions'] == users_instance.user_status_deny
    assert users_instance.user_access_check(user_id='testUser2', role_id='guest_role')['permissions'] == users_instance.user_status_deny
    assert users_instance.user_access_check(user_id='testUser2') == {'access': users_instance.user_status_allow}
    assert users_instance.user_access_check(user_id='testUser3', role_id='admin_role')['permissions'] == users_instance.user_status_deny
    assert users_instance.user_access_check(user_id='testUser3', role_id='guest_role')['permissions'] == users_instance.user_status_deny
    assert users_instance.user_access_check(user_id='testUser3') == {'access': users_instance.user_status_allow}
    assert users_instance.user_access_check(user_id='testUser4', role_id='admin_role')['permissions'] == users_instance.user_status_deny
    assert users_instance.user_access_check(user_id='testUser4', role_id='guest_role')['permissions'] == users_instance.user_status_deny
    assert users_instance.user_access_check(user_id='testUser4') == {'access': users_instance.user_status_allow}


@pytest.mark.order(6)
def test_authentication_user_denied(users_instance):
    """
    Verify response when the user is denied access.
    """
    assert users_instance.user_access_check(user_id='testUser20')['access'] == users_instance.user_status_deny
    assert users_instance.user_access_check(user_id='testUser20', role_id='admin_role')['access'] == users_instance.user_status_deny


@pytest.mark.order(7)
def test_authorization_user_denied(users_instance):
    """
    Verify response when the user is denied access.
    """
    assert users_instance.user_access_check(user_id='testUser21')['access'] == users_instance.user_status_allow
    assert users_instance.user_access_check(user_id='testUser21')['permissions'] == users_instance.user_status_allow
    assert users_instance.user_access_check(user_id='testUser21', role_id='admin_role')['permissions'] == users_instance.user_status_deny
