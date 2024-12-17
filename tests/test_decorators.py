"""
A test that verifies the decorators in the users module.
"""
import pytest


@pytest.mark.order(12)
def test_access_control_decorator(users_instance):
    """
    Verify the access control decorator for the user.
    """

    @users_instance.access_control(user_id='testUser24', flow='auth')
    def allowed_function(user_info: dict = None):
        return user_info

    assert allowed_function() == {'access': users_instance.user_status_allow}

    @users_instance.access_control(user_id='testUser25', flow='auth')
    def denied_function(user_info: dict = None):
        return user_info

    assert denied_function() is None

    @users_instance.access_control(user_id='testUser24', role_id='admin_role', flow='authz')
    def allowed_role_function(user_info: dict = None):
        return user_info

    assert allowed_role_function() == {
        'access': users_instance.user_status_allow, 'permissions': users_instance.user_status_allow, 'rate_limits': None
    }

    @users_instance.access_control(user_id='testUser25', role_id='admin_role', flow='authz')
    def denied_role_function(user_info: dict = None):
        return user_info

    assert denied_role_function() is None

    @users_instance.access_control(user_id='testUser124', flow='auth')
    def denied_unknown_user_function(user_info: dict = None):
        return user_info

    assert denied_unknown_user_function() is None
