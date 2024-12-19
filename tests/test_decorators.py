"""
A test that verifies the decorators in the users module.
"""
import random
import pytest
from mock import MagicMock


@pytest.mark.order(12)
def test_access_control_decorator(users_instance):
    """
    Verify the access control decorator for the user.
    """
    message = MagicMock()

    message.user.id = 'testUser24'
    message.chat.id = 'testUser24'
    message.message_id = random.randint(1, 9999)

    @users_instance.access_control(flow='auth')
    def allowed_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert allowed_function(message) == {'access': users_instance.user_status_allow}

    message.user.id = 'testUser25'
    message.chat.id = 'testUser25'
    message.message_id = random.randint(1, 9999)

    @users_instance.access_control(flow='auth')
    def denied_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert denied_function(message) is None

    message.user.id = 'testUser24'
    message.chat.id = 'testUser24'
    message.message_id = random.randint(1, 9999)

    @users_instance.access_control(role_id='admin_role', flow='authz')
    def allowed_role_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert allowed_role_function(message) == {
        'access': users_instance.user_status_allow, 'permissions': users_instance.user_status_allow, 'rate_limits': None
    }

    message.user.id = 'testUser124'
    message.chat.id = 'testUser124'
    message.message_id = random.randint(1, 9999)

    @users_instance.access_control(role_id='admin_role', flow='authz')
    def denied_role_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert denied_role_function(message) is None

    message.user.id = 'testUser124'
    message.chat.id = 'testUser124'
    message.message_id = random.randint(1, 9999)

    @users_instance.access_control(flow='auth')
    def denied_unknown_user_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert denied_unknown_user_function(message) is None
