"""
This module stores fixtures for performing tests.
"""
import json
from datetime import timedelta, datetime
import time
import requests
import pytest
import hvac
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
    """Wait for the vault server to start and return the url"""
    url = "http://0.0.0.0:8200"
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


@pytest.fixture(name="namespace", scope='session')
def fixture_name():
    """Returns the project namespace"""
    return "pytest"


@pytest.fixture(name="policy_path", scope='session')
def fixture_policy_path():
    """Returns the policy path"""
    return "tests/vault/policy.hcl"


@pytest.fixture(name="postgres_url", scope='session')
def fixture_postgres_url():
    """Returns the postgres url"""
    return "postgresql://{{username}}:{{password}}@postgres:5432/postgres?sslmode=disable"


@pytest.fixture(name="prepare_vault", scope='session')
def fixture_prepare_vault(vault_url, namespace, policy_path, postgres_url):
    """Returns the vault client"""
    client = hvac.Client(url=vault_url)
    init_data = client.sys.initialize()

    # Unseal the vault
    if client.sys.is_sealed():
        client.sys.submit_unseal_keys(keys=[init_data['keys'][0], init_data['keys'][1], init_data['keys'][2]])
    # Authenticate in the vault server using the root token
    client = hvac.Client(url=vault_url, token=init_data['root_token'])

    # Create policy
    with open(policy_path, 'rb') as policyfile:
        _ = client.sys.create_or_update_policy(
            name=namespace,
            policy=policyfile.read().decode("utf-8"),
        )

    # Create Namespace
    _ = client.sys.enable_secrets_engine(
        backend_type='kv',
        path=namespace,
        options={'version': 2}
    )

    # Prepare AppRole for the namespace
    client.sys.enable_auth_method(
        method_type='approle',
        path=namespace
    )
    _ = client.auth.approle.create_or_update_approle(
        role_name=namespace,
        token_policies=[namespace],
        token_type='service',
        secret_id_num_uses=0,
        token_num_uses=0,
        token_ttl='15s',
        bind_secret_id=True,
        token_no_default_policy=True,
        mount_point=namespace
    )
    approle_adapter = hvac.api.auth_methods.AppRole(client.adapter)

    # Prepare database engine configuration
    client.sys.enable_secrets_engine(
        backend_type='database',
        path='database'
    )

    # Configure database engine
    configuration = client.secrets.database.configure(
        name="postgresql",
        plugin_name="postgresql-database-plugin",
        verify_connection=False,
        allowed_roles=["test-role"],
        username="postgres",
        password="postgres",
        connection_url=postgres_url
    )
    print(f"Configured database engine: {configuration}")

    # Create role for the database
    role = client.secrets.database.create_role(
        name="test-role",
        db_name="postgresql",
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
        default_ttl="1h",
        max_ttl="24h"
    )
    print(f"Created role: {role}")

    # Return the role_id and secret_id
    return {
        'id': approle_adapter.read_role_id(role_name=namespace, mount_point=namespace)["data"]["role_id"],
        'secret-id': approle_adapter.generate_secret_id(role_name=namespace, mount_point=namespace)["data"]["secret_id"]
    }


@pytest.fixture(name="vault_instance", scope='session')
def fixture_vault_instance(vault_url, namespace, prepare_vault):
    """Returns client of the configurator"""
    return VaultClient(
        url=vault_url,
        namespace=namespace,
        auth={
            'type': 'approle',
            'approle': {
                'id': prepare_vault['id'],
                'secret-id': prepare_vault['secret-id']
            }
        }
    )


@pytest.fixture(name="timestamp_pattern", scope='session')
def fixture_timestamp_pattern():
    """Returns the timestamp pattern for compare date"""
    return r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$'


@pytest.fixture(name="users", scope='function')
def fixture_users(vault_instance,):
    """Fill in the configuration and data for the test users"""
    users = [
        # Test user1
        # - AUTHZ: allowed role1
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: requests limit PER HOUR exceeded
        # - RATE_LIMIT: restrictions on requests have not yet been applied
        'testUser1': {
            'status': 'allowed',
            'roles': ['admin_role'],
            'requests': {'requests_per_day': 10, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': [
                ('testUser1', 'testMessage1', 'testChat1', 'allowed', '{\'role_id\': \'admin_role\', \'status\': \'allowed\'}', datetime.now())
            ]
        },
        # Test user2
        # - AUTHZ: allowed role1 and role2
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: requests limit PER DAY exceeded
        # - RATE_LIMIT: restrictions on requests have not yet been applied
        'testUser2': {
            'status': 'allowed',
            'roles': ['financial_role', 'goals_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': [
                ('testUser2', 'testMessage2', 'testChat2', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now() - timedelta(hours=1)),
                ('testUser2', 'testMessage3', 'testChat2', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now() - timedelta(hours=2)),
            ]
        },
        # Test user3
        # - AUTHZ: allowed role1
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: requests limit PER DAY exceeded
        # - RATE_LIMIT: requests limit PER HOUR exceeded
        # - RATE_LIMIT: restrictions on requests have not yet been applied
        'testUser3': {
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 2, 'random_shift_minutes': 60},
            'requests_history': [
                ('testUser3', 'testMessage1', 'testChat3', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now()),
                ('testUser3', 'testMessage1', 'testChat3', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now() - timedelta(minutes=10)),
                ('testUser3', 'testMessage2', 'testChat3', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now() - timedelta(hours=1)),
                ('testUser3', 'testMessage2', 'testChat3', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now() - timedelta(hours=2)),                
            ]
        },
        # Test user4
        # - AUTHZ: allowed role1
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: rate limit timestamp exists for requests_per_hour but is expired (reset rate limit)
        'testUser4': {
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 60},
            'requests_history': [
                ('testUser4', 'testMessage1', 'testChat4', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now() - timedelta(hour=3), datetime.now() + timedelta(hour=1)),
                ('testUser4', 'testMessage1', 'testChat4', 'allowed', '{\'role_id\': \'financial_role\', \'status\': \'allowed\'}', datetime.now() - timedelta(hour=4)),
            ]
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
        ## NEED USER WITHOUT ROLES BUT WITH ACCESS!!!!!!
        # Test user4
        # - forbidden access for user
        {
            'name': 'testUser4',
            'status': 'denied',
            'roles': [],
            'requests': {}
        },

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
        vault=vault_instance,
        rate_limits=True
    )


@pytest.fixture(name="users_without_rl", scope='function')
def fixture_users_without_rl(vault_instance, users_attributes, users_data):
    """Returns an instance of the Users class with the rate limit controller disabled"""
    _ = users_attributes
    _ = users_data
    return Users(vault=vault_instance)
