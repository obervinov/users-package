# pylint: disable=too-few-public-methods,invalid-name
"""
A test that verifies the decorators in the users module.
"""
import random
import pytest
from mock import MagicMock


# pylint: disable=too-few-public-methods
class MockUser:
    """
    A mock user class.
    """
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


class MockChat:
    """
    A mock chat class.
    """
    def __init__(self, chat_id):
        self.id = chat_id


class MockMessage:
    """
    A mock message class.
    """
    def __init__(self, user_id, username, chat_id, message_id):
        self.user = MockUser(user_id, username)
        self.chat = MockChat(chat_id)
        self.message_id = message_id


class MockCall:
    """
    A mock call class.
    """
    def __init__(self, user_id, username, chat_id, message_id):
        self.message = MockMessage(user_id, username, chat_id, message_id)


@pytest.mark.order(12)
def test_access_control_decorator(users_instance):
    """
    Verify the access control decorator for the user.
    """
    message = MockMessage(user_id='testUser24', username='TestUser24', chat_id='testChat24', message_id=random.randint(1, 9999))

    @users_instance.access_control(flow='auth')
    def allowed_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert allowed_function(message) == {'access': users_instance.user_status_allow}

    message = MockMessage(user_id='testUser25', username='TestUser25', chat_id='testChat25', message_id=random.randint(1, 9999))

    @users_instance.access_control(flow='auth')
    def denied_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert denied_function(message) is None

    message = MockMessage(user_id='testUser24', username='TestUser24', chat_id='testChat24', message_id=random.randint(1, 9999))

    @users_instance.access_control(role_id='admin_role', flow='authz')
    def allowed_role_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert allowed_role_function(message) == {
        'access': users_instance.user_status_allow, 'permissions': users_instance.user_status_allow, 'rate_limits': None
    }

    message = MockMessage(user_id='testUser125', username='TestUser125', chat_id='testChat125', message_id=random.randint(1, 9999))

    @users_instance.access_control(role_id='admin_role', flow='authz')
    def denied_role_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert denied_role_function(message) is None

    message = MockMessage(user_id='testUser125', username='TestUser125', chat_id='testChat125', message_id=random.randint(1, 9999))

    @users_instance.access_control(flow='auth')
    def denied_unknown_user_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert denied_unknown_user_function(message) is None
