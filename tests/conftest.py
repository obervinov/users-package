"""
This module stores fixtures for performing tests.
"""
import os
import json
import subprocess
from datetime import timedelta, datetime
import time
import requests
import pytest
# pylint: disable=E0401
from vault import VaultClient
# pylint: disable=E0611
from users import Users


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


@pytest.fixture(name="vault_url", scope='session')
def fixture_vault_url():
    """Prepare a local environment or ci environment and return the URL of the Vault server"""
    # prepare vault for local environment
    if not os.getenv("CI"):
        command = (
            "vault=$(docker ps -a | grep vault | awk '{print $1}') && "
            "[ -n '$vault' ] && docker container rm -f $vault && "
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


@pytest.fixture(name="vault_approle", scope='session')
def fixture_vault_approle(vault_url, name, policy_path):
    """Prepare a temporary Vault instance and return the Vault client"""
    configurator = VaultClient(
                url=vault_url,
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
    return configurator.create_approle(
        name=name,
        path=namespace,
        policy=policy
    )


@pytest.fixture(name="vault_instance", scope='session')
def fixture_vault_instance(vault_url, vault_approle, name):
    """Returns an initialized vault instance"""
    return VaultClient(
        url=vault_url,
        name=name,
        approle=vault_approle
    )


@pytest.fixture(name="vault_configuration", scope='session')
def fixture_vault_configuration(vault_url, vault_approle, name):
    """Returns a dictionary for initializing the vault instance via the Users class"""
    return {
        'name': name,
        'url': vault_url,
        'approle': vault_approle
    }


@pytest.fixture(name="timestamp_pattern", scope='session')
def fixture_timestamp_pattern():
    """Returns the timestamp pattern for compare date"""
    return r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$'


@pytest.fixture(name="users_attributes", scope='function')
def fixture_users_attributes(vault_instance):
    """Fill in the configuration with test user attributes"""
    configurations = [
        # Test user1
        # - allowed all permissions
        # - limited request
        {
            'name': 'testUser1',
            'status': 'allowed',
            'roles': ['admin_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
        },
        # Test user2
        # - allowed role1 and role2
        # - limited request
        {
            'name': 'testUser2',
            'status': 'allowed',
            'roles': ['financial_role', 'goals_role'],
            'requests': {'requests_per_day': 30, 'requests_per_hour': 5, 'random_shift_minutes': 15}
        },
        # Test user3
        # - haven't roles
        # - hard limited request
        {
            'name': 'testUser3',
            'status': 'allowed',
            'roles': [],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 60}
        },
        # Test user4
        # - forbidden user
        {
            'name': 'testUser4',
            'status': 'denied',
            'roles': [],
            'requests': {}
        },
        # Test user5 for additional cases in rate limits controller
        {
            'name': 'testUser5',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 30, 'requests_per_hour': 3, 'random_shift_minutes': 15}
        },
        # Test user6 for additional cases in rate limits controller
        {
            'name': 'testUser6',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
        },
        # Test user6 for additional cases in rate limits controller
        {
            'name': 'testUser7',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
        },
        # Test user8 for additional cases in rate limits controller
        {
            'name': 'testUser8',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
        },
        # Test user9 for additional cases in rate limits controller
        {
            'name': 'testUser9',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
        },
        # Test user10 for additional cases in rate limits controller
        {
            'name': 'testUser10',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
        },
        # Test user11 for additional cases in rate limits controller (timer_watcher)
        {
            'name': 'testUser11',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15}
        },
        # Test user12 for additional cases in rate limits controller (timer_watcher)
        {
            'name': 'testUser12',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 30, 'requests_per_hour': 3, 'random_shift_minutes': 15}
        }
    ]
    for configuration in configurations:
        for key, value in configuration.items():
            if key in ['requests', 'roles']:
                _ = vault_instance.write_secret(
                    path=f'configuration/users/{configuration["name"]}',
                    key=key,
                    value=json.dumps(value)
                )
            else:
                _ = vault_instance.write_secret(
                    path=f'configuration/users/{configuration["name"]}',
                    key=key,
                    value=value
                )


@pytest.fixture(name="users_data", scope='function')
def fixture_users_data(vault_instance):
    """Fill in the test historical user data with request counters, applied rate limits timers."""
    # Test user1: detect and setup rate limits timestamp
    # - request limit exceeded
    # - restrictions on requests have not yet been applied
    data = [
        {
            'name': 'testUser1',
            'requests_history': [
                str(datetime.now() - timedelta(minutes=10*i)) for i in range(1, 2)
            ] + [
                str(datetime.now() - timedelta(hours=i)) for i in range(2, 11)
            ],
            'requests_ratelimits': {'end_time': None}
        },
        # Test user2: requests counters
        # - the request limit has not been exceeded
        # - restrictions on requests don't apply
        {
            'name': 'testUser2',
            'requests_history': [],
            'requests_ratelimits': {'end_time': None}
        },
        # Test user3: exist rate limit timestamp
        # - the request limit has been reset to zero
        # - restrictions on requests apply
        {
            'name': 'testUser3',
            'requests_history': [],
            'requests_ratelimits': {'end_time': f"{datetime.now() + timedelta(days=1)}"}
        },

        # Test user4: EMPTY (because configuration is forbidden access)

        # Test user5: exist rate limit timestamp
        # - the request limit has been reset to zero
        # - restrictions on requests apply
        {
            'name': 'testUser5',
            'requests_history': [],
            'requests_ratelimits': {'end_time': f"{datetime.now() + timedelta(hours=1)}"}
        },

        # Test user6: EMPTY (because configuration is forbidden access)

        # Test user7: detect and setup rate limits timestamps (for requests_per_day)
        # - request limit exceeded
        # - restrictions on requests have not yet been applied
        {
            'name': 'testUser7',
            'requests_history': [str(datetime.now() - timedelta(hours=i)) for i in range(2, 13)],
            'requests_ratelimits': {'end_time': None}
        },
        # Test user8: detect and setup rate limits timestamps (for requests_per_hour)
        # - request limit exceeded
        # - restrictions on requests have not yet been applied
        {
            'name': 'testUser8',
            'requests_history': [
                str(datetime.now() - timedelta(minutes=10*i)) for i in range(1, 2)
            ] + [
                str(datetime.now() - timedelta(hours=i)) for i in range(2, 3)
            ],
            'requests_ratelimits': {'end_time': None}
        },
        # Test user9: detect and setup rate limits timestamps (for both: requests_per_day and requests_per_hour)
        # - request limit exceeded
        # - restrictions on requests have not yet been applied
        {
            'name': 'testUser9',
            'requests_history': [
                str(datetime.now() - timedelta(minutes=10*i)) for i in range(1, 2)
            ] + [
                str(datetime.now() - timedelta(hours=i)) for i in range(2, 13)
            ],
            'requests_ratelimits': {'end_time': None}
        },
        # Test user10: reset expired rate limit
        # - the counter is reset to zero
        # - the speed limit timer has expired
        {
            'name': 'testUser10',
            'requests_history': [],
            'requests_ratelimits': {'end_time': str(datetime.now() - timedelta(hours=1))}
        },
        # Test user11: reset expired rate limit
        # - the counter is reset to zero
        # - the speed limit timer has expired
        {
            'name': 'testUser11',
            'requests_history': [
                str(datetime.now() - timedelta(minutes=15*i)) for i in range(1, 5)
            ] + [
                str(datetime.now() - timedelta(hours=i)) for i in range(20, 26)
            ],
            'requests_ratelimits': {'end_time': None}
        },
        # Test user12: reset expired rate limit
        # - the counter is reset to zero
        # - the speed limit timer has expired
        {
            'name': 'testUser12',
            'requests_history': [
                str(datetime.now() - timedelta(minutes=10*i)) for i in range(1, 2)
            ] + [
                str(datetime.now() - timedelta(hours=i)) for i in range(22, 34)
            ],
            'requests_ratelimits': {'end_time': None}
        }
    ]
    for user in data:
        for key, value in user.items():
            if key in ['requests_history', 'requests_ratelimits']:
                _ = vault_instance.write_secret(
                    path=f'data/users/{user["name"]}',
                    key=key,
                    value=json.dumps(value)
                )
            else:
                _ = vault_instance.write_secret(
                    path=f'data/users/{user["name"]}',
                    key=key,
                    value=value
                )


@pytest.fixture(name="users", scope='function')
def fixture_users(vault_instance, users_attributes, users_data):
    """Returns an instance of the Users class with the rate limit controller enabled"""
    _ = users_attributes
    _ = users_data
    return Users(
        vault=vault_instance
    )


@pytest.fixture(name="users_without_rl", scope='function')
def fixture_users_without_rl(vault_instance, users_attributes, users_data):
    """Returns an instance of the Users class with the rate limit controller disabled"""
    _ = users_attributes
    _ = users_data
    return Users(
        vault=vault_instance,
        rate_limits=False
    )
