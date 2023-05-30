"""
This module stores fixtures for performing tests.
"""
import os
import pytest
from vault import VaultClient
from users.users import UsersAuth


@pytest.fixture(name="url", scope='session')
def fixture_url():
    """Returns the vault url"""
    if os.getenv("CI"):
        return "http://localhost:8200"
    return "http://0.0.0.0:8200"


@pytest.fixture(name="name", scope='session')
def fixture_name():
    """Returns the project name"""
    return "testapp-1"


@pytest.fixture(name="policy_path", scope='session')
def fixture_policy_path():
    """Returns the policy path"""
    return "tests/vault/policy.hcl"


@pytest.fixture(name="vault", scope='session')
def fixture_vault(url, name, policy_path):
    """Prepare a storage instance for py tests and return the client"""
    configurator = VaultClient(
                url=url,
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
            url=url,
            name=name,
            approle=approle
    )


@pytest.fixture(name="userauth", scope='session')
def fixture_userauth(vault):
    """Returns userauth instance with vault and prepare test data"""
    test_data = {
        123456: 'allow',
        654321: 'deny'
    }
    for key, value in test_data.items():
        response = vault.write_secret(
            path='configuration/permissions',
            key=key,
            value=value
        )
        print(f"Prepared test data status: {response}")
    return UsersAuth(
        vault=vault
    )
