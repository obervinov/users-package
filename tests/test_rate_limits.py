"""
A test that checks the user request limit control function.
"""
import re
import datetime
import pytest


@pytest.mark.order(12)
def test_check_rl_counters_exceed_per_hour(timestamp_pattern, users_instance):
    """
    Checking behaviour when the user request counter is exceeded per hour.
    """
    now = datetime.datetime.now()
    user = users_instance.user_access_check(user_id='testUser5', role_id='admin_role')
    assert user['rate_limits'] is not None
    assert re.match(timestamp_pattern, str(user['rate_limits'])) is not None
    assert isinstance(user['rate_limits'], datetime.datetime)
    assert user['rate_limits'] >= now + datetime.timedelta(minutes=58)
    assert user['rate_limits'] < now + datetime.timedelta(hours=24)


@pytest.mark.order(13)
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


@pytest.mark.order(14)
def test_check_rl_counters_exceed_both(timestamp_pattern, users_instance):
    """
    Checking behaviour when the user request counter is exceeded for both counters (per hour and per day).
    """
    now = datetime.datetime.now()
    user = users_instance.user_access_check(user_id='testUser7', role_id='admin_role')
    assert user['rate_limits'] is not None
    assert re.match(timestamp_pattern, str(user['rate_limits'])) is not None
    assert isinstance(user['rate_limits'], datetime.datetime)
    assert user['rate_limits'] >= now + datetime.timedelta(minutes=1395)
    assert user['rate_limits'] <= now + datetime.timedelta(hours=48)


@pytest.mark.order(15)
def test_check_rl_counters_do_not_exceed(users_instance):
    """
    Checking behaviour when the user request counter does not exceed any of the counters.
    """
    # First check
    user = users_instance.user_access_check(user_id='testUser11', role_id='admin_role')
    assert user['rate_limits'] is None
    # Second check
    user = users_instance.user_access_check(user_id='testUser11', role_id='admin_role')
    assert user['rate_limits'] is None
    # Third check
    user = users_instance.user_access_check(user_id='testUser11', role_id='admin_role')
    assert user['rate_limits'] is None
