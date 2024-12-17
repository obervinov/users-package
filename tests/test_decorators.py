"""
A test that verifies the decorators in the users module.
"""
import pytest


@pytest.mark.order(12)
def test_access_control_decorator(users_instance):
    """
    Verify the access control decorator for the user.
    """

    @users_instance.access_control_decorator(user_id='testUser24', flow='auth')
    def allowed_function():
        return 'test'

    assert allowed_function() == 'test'

    @users_instance.access_control_decorator(user_id='testUser25', flow='auth')
    def denied_function():
        return 'test'

    assert denied_function() is None

    @users_instance.access_control_decorator(user_id='testUser24', role_id='admin_role', flow='authz')
    def allowed_role_function():
        return 'test'

    assert allowed_role_function() == 'test'

    @users_instance.access_control_decorator(user_id='testUser25', role_id='admin_role', flow='authz')
    def denied_role_function():
        return 'test'

    assert denied_role_function() is None

    @users_instance.access_control_decorator(user_id='testUser124', flow='auth')
    def denied_unknown_user_function():
        return 'test'

    assert denied_unknown_user_function() is None
