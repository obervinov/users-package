"""
A test that checks the user request limit control function.
"""
import re
import datetime
import pytest


@pytest.mark.order(11)
def test_check_rl_counters_exceed_per_hour(timestamp_pattern, users_instance):
    """
    Checking behaviour when the user request counter is exceeded per hour.
    """
    now = datetime.datetime.now()
    user = users_instance.user_access_check(user_id='testUser5', role_id='admin_role')
    assert user['rate_limits'] is not None
    assert re.match(timestamp_pattern, str(user['rate_limits'])) is not None
    assert isinstance(user['rate_limits'], datetime.datetime)
    assert user['rate_limits'] >= now + datetime.timedelta(hours=1)
    assert user['rate_limits'] < now + datetime.timedelta(hours=24)


@pytest.mark.order(12)
def test_check_rl_counters_exceed_per_day(timestamp_pattern, users_instance):
    """
    Checking behaviour when the user request counter is exceeded per day.
    """
    now = datetime.datetime.now()
    user = users_instance.user_access_check(user_id='testUser6', role_id='admin_role')
    assert user['rate_limits'] is not None
    assert re.match(timestamp_pattern, str(user['rate_limits'])) is not None
    assert isinstance(user['rate_limits'], datetime.datetime)
    assert user['rate_limits'] >= now + datetime.timedelta(hours=24)
    assert user['rate_limits'] <= now + datetime.timedelta(hours=48)


@pytest.mark.order(13)
def test_check_rl_counters_exceed_both(timestamp_pattern, users_instance):
    """
    Checking behaviour when the user request counter is exceeded for both counters (per hour and per day).
    """
    now = datetime.datetime.now()
    user = users_instance.user_access_check(user_id='testUser7', role_id='admin_role')
    assert user['rate_limits'] is not None
    assert re.match(timestamp_pattern, str(user['rate_limits'])) is not None
    assert isinstance(user['rate_limits'], datetime.datetime)
    assert user['rate_limits'] >= now + datetime.timedelta(hours=25)
    assert user['rate_limits'] <= now + datetime.timedelta(hours=48)


# @pytest.mark.order(7)
# def test_check_rl_counters_increase(vault_instance):
#     """
#     The function checks the situation with how the counter works.
#     """
#     user_id = 'testUser2'

#     # increase the request counter by 1
#     rl_controller = RateLimiter(
#         vault=vault_instance,
#         user_id=user_id
#     )
#     _ = rl_controller.determine_rate_limit()

#     # increase the request counter by 1 and get user info
#     rl_controller = RateLimiter(
#         vault=vault_instance,
#         user_id=user_id
#     )
#     _ = rl_controller.determine_rate_limit()
#     requests_counters = vault_instance.read_secret(
#         path=f"data/users/{user_id}",
#         key="requests_counters"
#     )
#     assert json.loads(requests_counters) == {'requests_per_day': 1, 'requests_per_hour': 1}


# @pytest.mark.order(8)
# def test_check_rl_timestamps(vault_instance, timestamp_pattern):
#     """
#     The function checks the situation with what is returned in the response
#     from the rl controller when the rate limit is applied.
#     """
#     # day_end, hour_end
#     users_cases = [
#         'testUser3',
#         'testUser5'
#     ]
#     for user_id in users_cases:
#         rl_controller = RateLimiter(
#             vault=vault_instance,
#             user_id=user_id
#         )
#         result = rl_controller.determine_rate_limit()
#         end_time = result.get('end_time', None)
#         assert end_time is not None, f"end_time is not present in the result for {user_id}"
#         assert re.match(
#             timestamp_pattern,
#             end_time
#         ), f"end_time '{end_time}' does not match the expected pattern for {user_id}"


# @pytest.mark.order(9)
# def test_check_rl_apply(vault_instance, timestamp_pattern):
#     """
#     The function checks the situation when the limits are exhausted and you need to apply the rate limit.
#     """
#     # day_end, hour_end, both
#     users_cases = [
#         'testUser7',
#         'testUser8',
#         'testUser9'
#     ]
#     for user_id in users_cases:
#         rl_controller = RateLimiter(
#             vault=vault_instance,
#             user_id=user_id
#         )
#         result = rl_controller.determine_rate_limit()
#         end_time = result.get('end_time', None)
#         assert end_time is not None, f"end_time is not present in the result for {user_id}"
#         assert re.match(
#             timestamp_pattern,
#             end_time
#         ), f"end_time '{end_time}' does not match the expected pattern for {user_id}"


# @pytest.mark.order(10)
# def test_check_rl_reset(vault_instance):
#     """
#     The function checks the situation when the time for applying the speed limit
#     has already expired and it needs to be reset.
#     """
#     user_id = 'testUser10'
#     rl_controller = RateLimiter(
#         vault=vault_instance,
#         user_id=user_id
#     )
#     result = rl_controller.determine_rate_limit()
#     end_time = result.get('end_time', None)
#     assert end_time is None, f"end_time is not None in the result for {user_id}"


# @pytest.mark.order(12)
# def test_check_rl_counters_watching_decrease_per_hour(vault_instance):
#     """
#     The function checks how updating and resetting counters works over time (by hour).
#     """
#     user_id = 'testUser11'
#     rl_controller = RateLimiter(
#         vault=vault_instance,
#         user_id=user_id
#     )
#     _ = rl_controller.determine_rate_limit()
#     requests_counters = vault_instance.read_secret(
#         path=f"data/users/{user_id}",
#         key="requests_counters"
#     )
#     assert json.loads(requests_counters) == {'requests_per_day': 8, 'requests_per_hour': 3}


# @pytest.mark.order(13)
# def test_check_rl_counters_watching_decrease_per_day(vault_instance):
#     """
#     The function checks how updating and resetting counters works over time (by day).
#     """
#     user_id = 'testUser12'
#     rl_controller = RateLimiter(
#         vault=vault_instance,
#         user_id=user_id
#     )
#     _ = rl_controller.determine_rate_limit()
#     requests_counters = vault_instance.read_secret(
#         path=f"data/users/{user_id}",
#         key="requests_counters"
#     )
#     assert json.loads(requests_counters) == {'requests_per_day': 3, 'requests_per_hour': 1}


# @pytest.mark.order(17)
# def test_check_entrypoint_rl_applied(users, timestamp_pattern):
#     """
#     Verify that the main entry point for user verification correctly applies rate limits
#     and matches the end_time using a regular expression.
#     """
#     user = 'testUser5'
#     result = users.user_access_check(user_id=user, role_id='financial_role')

#     assert result['access'] == users.user_status_allow
#     assert result['permissions'] == users.user_status_allow

#     end_time = result['rate_limits']['end_time']
#     assert re.match(timestamp_pattern, end_time) is not None


# @pytest.mark.order(18)
# def test_check_entrypoint_rl_not_applied(users):
#     """
#     Verify that the main entry point for user verification correctly handles the case
#     where rate limits are not applied.
#     """
#     user = 'testUser2'
#     assert users.user_access_check(user_id=user, role_id='financial_role') == {
#                 'access': users.user_status_allow,
#                 'permissions': users.user_status_allow,
#                 'rate_limits': {'end_time': None}
#     }
