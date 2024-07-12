"""
This module stores fixtures for performing tests.
"""
import json
from datetime import timedelta, datetime
import time
import requests
import pytest
import hvac
import psycopg2
from vault import VaultClient
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
    return "pytests"


@pytest.fixture(name="policy_path", scope='session')
def fixture_policy_path():
    """Returns the policy path"""
    return "tests/vault/policy.hcl"


@pytest.fixture(name="psql_tables_path", scope='session')
def fixture_psql_tables_path():
    """Returns the path to the postgres sql file with tables"""
    return "tests/postgres/tables.sql"


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
    statement = (
        "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; "
        "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"{{name}}\"; "
        "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO \"{{name}}\";"
    )
    role = client.secrets.database.create_role(
        name="test-role",
        db_name="postgresql",
        creation_statements=statement,
        default_ttl="1h",
        max_ttl="24h"
    )
    print(f"Created role: {role}")

    # Return the role_id and secret_id
    return {
        'id': approle_adapter.read_role_id(role_name=namespace, mount_point=namespace)["data"]["role_id"],
        'secret-id': approle_adapter.generate_secret_id(role_name=namespace, mount_point=namespace)["data"]["secret_id"]
    }


@pytest.fixture(name="postgres_instance", scope='session')
def fixture_postgres_instance(psql_tables_path):
    """Prepare the postgres database, return the connection and cursor"""
    # Prepare database for tests
    psql_connection = psycopg2.connect(
        host='0.0.0.0',
        port=5432,
        user='postgres',
        password='postgres',
        dbname='postgres'
    )
    psql_cursor = psql_connection.cursor()
    with open(psql_tables_path, 'r', encoding='utf-8') as sql_file:
        sql_script = sql_file.read()
        psql_cursor.execute(sql_script)
        psql_connection.commit()
    return psql_connection, psql_cursor


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


@pytest.fixture(name="database_secret", scope='session')
def fixture_database_secret(vault_instance):
    """Returns the database secret"""
    secret_path = 'configuration/database'
    _ = vault_instance.kv2engine.write_secret(
        path=secret_path,
        key='dbname',
        value='postgres'
    )
    _ = vault_instance.kv2engine.write_secret(
        path=secret_path,
        key='host',
        value='0.0.0.0'
    )
    _ = vault_instance.kv2engine.write_secret(
        path=secret_path,
        key='port',
        value='5432'
    )


@pytest.fixture(name="users", scope='session')
def fixture_users(vault_instance, postgres_instance):
    """Fill in the configuration and data for the test users"""
    users = [
        #
        # Test user1
        # - AUTHZ: allowed role1
        # - RATE_LIMIT: limited requests
        {
            'name': 'testUser1',
            'status': 'allowed',
            'roles': ['admin_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': []
        },
        #
        # Test user2
        # - AUTHZ: allowed role1 and role2
        # - RATE_LIMIT: limited requests
        {
            'name': 'testUser2',
            'status': 'allowed',
            'roles': ['financial_role', 'goals_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': []
        },
        #
        # Test user3
        # - AUTHZ: allowed role1
        # - RATE_LIMIT: limited requests
        {
            'name': 'testUser3',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': []
        },
        #
        # Test user4
        # - AUTHZ: allowed role1
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: rate limit timestamp exists for requests_per_hour but is expired (reset rate limit)
        {
            'name': 'testUser4',
            'status': 'allowed',
            'roles': ['financial_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': []
        },
        #
        # Test user5
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: requests limit PER HOUR exceeded after next request
        # - RATE_LIMIT: restrictions on requests have not yet been applied
        {
            'name': 'testUser5',
            'status': 'allowed',
            'roles': ['admin_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': [
                ('testUser5', 'testMessage1', 'testChat5', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now())
            ]
        },
        #
        # Test user6
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: requests limit PER DAY exceeded
        # - RATE_LIMIT: restrictions on requests have not yet been applied
        {
            'name': 'testUser6',
            'status': 'allowed',
            'roles': ['admin_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': [
                ('testUser6', 'testMessage1', 'testChat6', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=3)),
                ('testUser6', 'testMessage1', 'testChat6', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=4)),
                ('testUser6', 'testMessage1', 'testChat6', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=5)),
                ('testUser6', 'testMessage1', 'testChat6', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=6), datetime.now() + timedelta(hours=24)),
            ]
        },
        #
        # Test user7
        # - RATE_LIMIT: limited requests
        # - RATE_LIMIT: requests limit PER DAY exceeded
        # - RATE_LIMIT: requests limit PER HOUR exceeded
        # - RATE_LIMIT: restrictions on requests have not yet been applied
        {
            'name': 'testUser7',
            'status': 'allowed',
            'roles': ['admin_role'],
            'requests': {'requests_per_day': 3, 'requests_per_hour': 1, 'random_shift_minutes': 15},
            'requests_history': [
                ('testUser7', 'testMessage1', 'testChat7', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=1)),
                ('testUser7', 'testMessage1', 'testChat7', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=1), datetime.now() + timedelta(hours=1, minutes=15)),
                ('testUser7', 'testMessage1', 'testChat7', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=3)),
                ('testUser7', 'testMessage1', 'testChat7', 'allowed', '{"role_id": "admin_role", "status": "allowed"}', datetime.now() - timedelta(hours=4), datetime.now() + timedelta(hours=24)),
            ]
        },
        #
        # Test user20
        # - AUTHN: denied
        # - AUTHZ: denied
        {
            'name': 'testUser20',
            'status': 'denied',
            'roles': [],
            'requests': []
        },
        #
        # Test user21
        # - AUTHN: allowed
        # - AUTHZ: denied
        {
            'name': 'testUser21',
            'status': 'allowed',
            'roles': [],
            'requests': []
        }
    ]
    psql_connection, psql_cursor = postgres_instance
    for user in users:
        for key, value in user.items():
            if key in ['requests', 'roles']:
                _ = vault_instance.kv2engine.write_secret(
                    path=f'configuration/users/{user["name"]}',
                    key=key,
                    value=json.dumps(value)
                )
            elif key == 'status':
                _ = vault_instance.kv2engine.write_secret(
                    path=f'configuration/users/{user["name"]}',
                    key=key,
                    value=value
                )
            elif key == 'requests_history' and len(key) > 0:
                for row in value:
                    if len(row) == 6:
                        _ = psql_cursor.execute(
                            "INSERT INTO users_requests (user_id, message_id, chat_id, authentication, \"authorization\", timestamp) "
                            f"VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}')"
                        )
                    elif len(row) == 7:
                        _ = psql_cursor.execute(
                            "INSERT INTO users_requests (user_id, message_id, chat_id, authentication, \"authorization\", timestamp, rate_limits) "
                            f"VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}', '{row[6]}')"
                        )
                    psql_connection.commit()


@pytest.fixture(name="users_instance", scope='function')
def fixture_users_instance(vault_instance, users, database_secret):
    """Returns an instance of the Users class with the rate limit controller enabled"""
    _ = users
    _ = database_secret
    return Users(
        vault=vault_instance,
        rate_limits=True,
        storage={'db_role': 'test-role'}
    )


@pytest.fixture(name="users_instance_without_rl", scope='function')
def fixture_users_instance_without_rl(vault_instance, users, database_secret):
    """Returns an instance of the Users class with the rate limit controller disabled"""
    _ = users
    _ = database_secret
    return Users(
        vault=vault_instance,
        storage={'db_role': 'test-role'}
    )
