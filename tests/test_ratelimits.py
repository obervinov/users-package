"""
A test that checks the user request limit control function.
"""
import re
import pytest
from users.ratelimits import RateLimiter


@pytest.mark.order(6)
def test_check_rl_counters_exceed(timestamp_pattern, vault_instance):
    """
    The function checks the situation of who the request counter is above.
    """
    users_cases = [
        'testUser1',
        'testUser7',
        'testUser8'
    ]
    for user in users_cases:
        rl_controller = RateLimiter(
            vault=vault_instance,
            user_id=user
        )
        result = rl_controller.determine_rate_limit()
        end_time = result.get('end_time', None)
        assert end_time is not None, f"end_time is not present in the result for {user}"
        assert re.match(
            timestamp_pattern,
            end_time
        ), f"end_time '{end_time}' does not match the expected pattern for {user}"


@pytest.mark.order(7)
def test_check_rl_counters_increase(vault_instance):
    """
    The function checks the situation with how the counter works.
    """
    user_id = 'testUser2'

    # increase the request counter by 1
    rl_controller = RateLimiter(
        vault=vault_instance,
        user_id=user_id
    )
    _ = rl_controller.determine_rate_limit()

    # increase the request counter by 1 and get user info
    rl_controller = RateLimiter(
        vault=vault_instance,
        user_id=user_id
    )
    _ = rl_controller.determine_rate_limit()

    assert vault_instance.read_secret(
        path=f"data/users/{user_id}",
        key="requests_counters"
    ) == {'requests_per_day': 2, 'requests_per_hour': 2}


@pytest.mark.order(8)
def test_check_rl_timestamps(vault_instance, timestamp_pattern):
    """
    The function checks the situation with what is returned in the response
    from the rl controller when the rate limit is applied.
    """
    # day_end, hour_end
    users_cases = [
        'testUser3',
        'testUser5'
    ]
    for user_id in users_cases:
        rl_controller = RateLimiter(
            vault=vault_instance,
            user_id=user_id
        )
        result = rl_controller.determine_rate_limit()
        end_time = result.get('end_time', None)
        assert end_time is not None, f"end_time is not present in the result for {user_id}"
        assert re.match(
            timestamp_pattern,
            end_time
        ), f"end_time '{end_time}' does not match the expected pattern for {user_id}"


@pytest.mark.order(9)
def test_check_rl_apply(vault_instance, timestamp_pattern):
    """
    The function checks the situation when the limits are exhausted and you need to apply the rate limit.
    """
    # day_end, hour_end, both
    users_cases = [
        'testUser7',
        'testUser8',
        'testUser9'
    ]
    for user_id in users_cases:
        rl_controller = RateLimiter(
            vault=vault_instance,
            user_id=user_id
        )
        result = rl_controller.determine_rate_limit()
        end_time = result.get('end_time', None)
        assert end_time is not None, f"end_time is not present in the result for {user_id}"
        assert re.match(
            timestamp_pattern,
            end_time
        ), f"end_time '{end_time}' does not match the expected pattern for {user_id}"


@pytest.mark.order(10)
def test_check_rl_reset(vault_instance):
    """
    The function checks the situation when the time for applying the speed limit
    has already expired and it needs to be reset.
    """
    user_id = 'testUser10'
    rl_controller = RateLimiter(
        vault=vault_instance,
        user_id=user_id
    )
    result = rl_controller.determine_rate_limit()
    end_time = result.get('end_time', None)
    assert end_time is None, f"end_time is not None in the result for {user_id}"
