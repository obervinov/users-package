# pylint: disable=too-few-public-methods,invalid-name
"""
A test that verifies the decorators in the users module.
"""
import random
import pytest


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
    def __init__(self, chat_id, message_id):
        self.chat = MockChat(chat_id)
        self.message_id = message_id


class MockCall:
    """
    A mock call class.
    """
    def __init__(self, chat_id, message_id):
        self.message = MockMessage(chat_id, message_id)


@pytest.mark.order(12)
def test_access_control_decorator(users_instance):
    """
    Verify the access control decorator for the user.
    """

    # the user is allowed access to the bot
    message = MockMessage(chat_id='testUser24', message_id=random.randint(1, 9999))

    @users_instance.access_control(flow='auth')
    def allowed_exist_user_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert allowed_exist_user_function(message) == {'access': users_instance.user_status_allow}

    # the user is explicitly blocked from accessing the bot
    message = MockMessage(chat_id='testUser25', message_id=random.randint(1, 9999))

    @users_instance.access_control(flow='auth')
    def blocked_exist_user_function(message: object, access_result: dict = None):
        print(message)
        print(access_result)
        return 'unauthorized access'
    assert blocked_exist_user_function(message) is None

    # user has a specified access role
    message = MockMessage(chat_id='testUser24', message_id=random.randint(1, 9999))

    @users_instance.access_control(role_id='admin_role', flow='authz')
    def allowed_exist_user_with_role_function(message: object, access_result: dict = None):
        print(message)
        return access_result
    assert allowed_exist_user_with_role_function(message) == {
        'access': users_instance.user_status_allow, 'permissions': users_instance.user_status_allow, 'rate_limits': None
    }

    # the user has a role but not the one requested
    message = MockMessage(chat_id='testUser24', message_id=random.randint(1, 9999))

    @users_instance.access_control(role_id='other_role', flow='authz')
    def allowed_exist_user_without_role_function(message: object, access_result: dict = None):
        print(message)
        print(access_result)
        return 'unauthorized access'
    assert allowed_exist_user_without_role_function(message) is None

    # the user is explicitly blocked from access and the user has no roles
    message = MockMessage(chat_id='testUser25', message_id=random.randint(1, 9999))

    @users_instance.access_control(role_id='admin_role', flow='authz')
    def blocked_exist_user_without_role_function(message: object, access_result: dict = None):
        print(message)
        print(access_result)
        return 'unauthorized access'
    assert blocked_exist_user_without_role_function(message) is None

    # non-existent random user configuration
    random_user_id = f"testUser{random.randint(100, 10000)}"
    message = MockMessage(chat_id=random_user_id, message_id=random.randint(1, 9999))

    @users_instance.access_control(flow='auth')
    def does_not_exist_user_function(message: object, access_result: dict = None):
        print(message)
        print(access_result)
        return 'unauthorized access'
    assert does_not_exist_user_function(message) is None

    # non-existent random user configuration without role
    random_user_id = f"testUser{random.randint(100, 10000)}"
    message = MockMessage(chat_id=random_user_id, message_id=random.randint(1, 9999))

    @users_instance.access_control(role_id='admin_role', flow='authz')
    def does_not_exist_user_without_role_function(message: object, access_result: dict = None):
        print(message)
        print(access_result)
        return 'unauthorized access'
    assert does_not_exist_user_without_role_function(message) is None
