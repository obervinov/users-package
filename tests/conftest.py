"""
This module stores fixtures for performing tests.
"""
import os
import subprocess
from datetime import timedelta, datetime
import time
import requests
import pytest
# pylint: disable=E0401
from vault import VaultClient
# pylint: disable=E0611
from users.users import Users


def pytest_configure(config):
    """
    Configure Pytest by adding a custom marker for setting the execution order of tests.

    This function is called during Pytest's configuration phase and is used to extend Pytest's
    functionality by adding custom markers. In this case, it adds a "order" marker to specify
    the execution order of tests.

    Parameters:
    - config (object): The Pytest configuration object.

    Example Usage:
    @pytest.mark.order(1)
    def test_example():
        # test code
    """
    config.addinivalue_line("markers", "order: Set the execution order of tests")


@pytest.fixture(name="prepare_environment", scope='session')
def fixture_prepare_environment():
    """Prepare a local environment or ci environment and return the URL of the Vault server"""
    # prepare vault for local environment
    if not os.getenv("CI"):
        command = (
            "docker compose -f docker-compose.yml down && "
            "docker volume rm $(docker volume ls -q) && "
            "docker compose -f docker-compose.yml up -d"
        )
        with subprocess.Popen(command, shell=True):
            print("Running vault server")
        url = "http://0.0.0.0:8200"
    # prepare vault for ci environment
    else:
        url = "http://localhost:8200"

    # checking the availability of the vault server
    while True:
        try:
            response = requests.get(url=url, timeout=3)
            if 200 <= response.status_code < 500:
                break
        except requests.exceptions.RequestException as exception:
            print(f"Waiting for the vault server: {exception}")
            time.sleep(5)

    return url


@pytest.fixture(name="name", scope='session')
def fixture_name():
    """Returns the project name"""
    return "pytest"


@pytest.fixture(name="policy_path", scope='session')
def fixture_policy_path():
    """Returns the policy path"""
    return "tests/vault/policy.hcl"


@pytest.fixture(name="vault", scope='session')
def fixture_vault(prepare_environment, name, policy_path):
    """Prepare a temporary Vault instance and return the Vault client"""
    configurator = VaultClient(
                url=prepare_environment,
                name=name,
                new=True
    )
    namespace = configurator.create_namespace(
            name=name
    )
    policy = configurator.create_policy(
            name=name,
            path=policy_path
        )
    approle = configurator.create_approle(
        name=name,
        path=namespace,
        policy=policy
    )
    return VaultClient(
            url=prepare_environment,
            name=name,
            approle=approle
    )


@pytest.fixture(name="timestamp_pattern", scope='session')
def fixture_timestamp_pattern():
    """Returns the timestamp pattern for compare date"""
    return r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$'


@pytest.fixture(name="users_attributes", scope='function')
def fixture_users_attributes(vault):
    """Fill in the configuration with test user attributes"""
    # Test user1
    # - allowed all permissions
    # - limited request
    test_user1 = {
        'status': 'allowed',
        'roles': ['admin_role'],
        'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
    }
    # Test user2
    # - allowed role1 and role2
    # - limited request
    test_user2 = {
        'status': 'allowed',
        'roles': ['financial_role', 'goals_role'],
        'requests': {'requests_per_day': 30, 'requests_per_hour': 5, 'random_shift_minutes': 15}
    }
    # Test user3
    # - haven't roles
    # - hard limited request
    test_user3 = {
        'status': 'allowed',
        'roles': [],
        'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 60}
    }
    # Test user4
    # - forbidden user
    test_user4 = {
        'status': 'denied',
        'roles': [],
        'requests': {}
    }
    # Test user5 for additional cases in rate limits controller
    test_user5 = {
        'status': 'allowed',
        'roles': ['financial_role'],
        'requests': {'requests_per_day': 30, 'requests_per_hour': 3, 'random_shift_minutes': 15}
    }
    # Test user6 for additional cases in rate limits controller
    test_user6 = {
        'status': 'allowed',
        'roles': ['financial_role'],
        'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
    }
    # Test user6 for additional cases in rate limits controller
    test_user7 = {
        'status': 'allowed',
        'roles': ['financial_role'],
        'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
    }
    # Test user8 for additional cases in rate limits controller
    test_user8 = {
        'status': 'allowed',
        'roles': ['financial_role'],
        'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
    }
    # Test user9 for additional cases in rate limits controller
    test_user9 = {
        'status': 'allowed',
        'roles': ['financial_role'],
        'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
    }
    # Test user10 for additional cases in rate limits controller
    test_user10 = {
        'status': 'allowed',
        'roles': ['financial_role'],
        'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
    }
    for key, value in test_user1.items():
        _ = vault.write_secret(
            path='configuration/users/testUser1',
            key=key,
            value=value
        )
    for key, value in test_user2.items():
        _ = vault.write_secret(
            path='configuration/users/testUser2',
            key=key,
            value=value
        )
    for key, value in test_user3.items():
        _ = vault.write_secret(
            path='configuration/users/testUser3',
            key=key,
            value=value
        )
    for key, value in test_user4.items():
        _ = vault.write_secret(
            path='configuration/users/testUser4',
            key=key,
            value=value
        )
    for key, value in test_user5.items():
        _ = vault.write_secret(
            path='configuration/users/testUser5',
            key=key,
            value=value
        )
    for key, value in test_user6.items():
        _ = vault.write_secret(
            path='configuration/users/testUser6',
            key=key,
            value=value
        )
    for key, value in test_user7.items():
        _ = vault.write_secret(
            path='configuration/users/testUser7',
            key=key,
            value=value
        )
    for key, value in test_user8.items():
        _ = vault.write_secret(
            path='configuration/users/testUser8',
            key=key,
            value=value
        )
    for key, value in test_user9.items():
        _ = vault.write_secret(
            path='configuration/users/testUser9',
            key=key,
            value=value
        )
    for key, value in test_user10.items():
        _ = vault.write_secret(
            path='configuration/users/testUser10',
            key=key,
            value=value
        )


@pytest.fixture(name="users_data", scope='function')
def fixture_users_data(vault):
    """Fill in the test historical user data with request counters, applied rate limits timers."""
    # Test user1: detect and setup rate limits timestamp
    # - request limit exceeded
    # - restrictions on requests have not yet been applied
    test_user1 = {
        'requests_counters': {'requests_per_day': 11, 'requests_per_hour': 2},
        'rate_limits': {'end_time': None}
    }
    # Test user2: requests counters
    # - the request limit has not been exceeded
    # - restrictions on requests don't apply
    test_user2 = {
        'requests_counters': {'requests_per_day': 0, 'requests_per_hour': 0},
        'rate_limits': {'end_time': None}
    }
    # Test user3: exist rate limit timestamp
    # - the request limit has been reset to zero
    # - restrictions on requests apply
    test_user3 = {
        'requests_counters': {'requests_per_day': 0, 'requests_per_hour': 0},
        'rate_limits': {'end_time': f"{datetime.now() + timedelta(days=1)}"}
    }

    # Test user4: EMPTY

    # Test user5: exist rate limit timestamp
    # - the request limit has been reset to zero
    # - restrictions on requests apply
    test_user5 = {
        'requests_counters': {'requests_per_day': 0, 'requests_per_hour': 0},
        'rate_limits': {'end_time': f"{datetime.now() + timedelta(hours=1)}"}
    }

    # Test user6: EMPTY

    # Test user7: detect and setup rate limits timestamps (for requests_per_day)
    # - request limit exceeded
    # - restrictions on requests have not yet been applied
    test_user7 = {
        'requests_counters': {'requests_per_day': 10, 'requests_per_hour': 0},
        'rate_limits': {'end_time': None}
    }
    # Test user8: detect and setup rate limits timestamps (for requests_per_hour)
    # - request limit exceeded
    # - restrictions on requests have not yet been applied
    test_user8 = {
        'requests_counters': {'requests_per_day': 1, 'requests_per_hour': 1},
        'rate_limits': {'end_time': None}
    }
    # Test user9: detect and setup rate limits timestamps (for both: requests_per_day and requests_per_hour)
    # - request limit exceeded
    # - restrictions on requests have not yet been applied
    test_user9 = {
        'requests_counters': {'requests_per_day': 10, 'requests_per_hour': 1},
        'rate_limits': {'end_time': None}
    }
    # Test user10: reset expired rate limit
    # - the counter is reset to zero
    # - the speed limit timer has expired
    test_user10 = {
        'requests_counters': {'requests_per_day': 0, 'requests_per_hour': 0},
        'rate_limits': {'end_time': str(datetime.now() - timedelta(hours=1))}
    }
    for key, value in test_user1.items():
        _ = vault.write_secret(
            path='data/users/testUser1',
            key=key,
            value=value
        )
    for key, value in test_user2.items():
        _ = vault.write_secret(
            path='data/users/testUser2',
            key=key,
            value=value
        )
    for key, value in test_user3.items():
        _ = vault.write_secret(
            path='data/users/testUser3',
            key=key,
            value=value
        )
    for key, value in test_user5.items():
        _ = vault.write_secret(
            path='data/users/testUser5',
            key=key,
            value=value
        )
    for key, value in test_user7.items():
        _ = vault.write_secret(
            path='data/users/testUser7',
            key=key,
            value=value
        )
    for key, value in test_user8.items():
        _ = vault.write_secret(
            path='data/users/testUser8',
            key=key,
            value=value
        )
    for key, value in test_user9.items():
        _ = vault.write_secret(
            path='data/users/testUser9',
            key=key,
            value=value
        )
    for key, value in test_user10.items():
        _ = vault.write_secret(
            path='data/users/testUser10',
            key=key,
            value=value
        )


@pytest.fixture(name="users", scope='function')
def fixture_users(vault, users_attributes, users_data):
    """Returns an instance of the Users class with the rate limit controller enabled"""
    _ = users_attributes
    _ = users_data
    return Users(
        vault=vault
    )


@pytest.fixture(name="users_without_rl", scope='function')
def fixture_users_without_rl(vault, users_attributes, users_data):
    """Returns an instance of the Users class with the rate limit controller disabled"""
    _ = users_attributes
    _ = users_data
    return Users(
        vault=vault,
        rate_limits=False
    )
