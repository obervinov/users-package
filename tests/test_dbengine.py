"""This file contains tests for check connection to database with Vault Database Engine"""
import pytest

@pytest.mark.order(17)
def test_check_dbengine_connection(users_instance_dbengine):
    """
    Verify the connection to the database engine.
    """
    # Check the storage class input parameters
    assert users_instance_dbengine.storage.db_connection is None
    assert isinstance(users_instance_dbengine.storage.vault, dict)
    assert isinstance(users_instance_dbengine.storage.vault.instance, object)
    assert isinstance(users_instance_dbengine.storage.vault.role, str)
    assert users_instance_dbengine.storage.vault.role == 'test-role'
    # Check the connection to the database engine
    assert users_instance_dbengine.storage.connection is not None
    assert users_instance_dbengine.storage.cursor is not None
    # Check query execution
    users_instance_dbengine.storage.cursor.execute("SELECT id FROM users LIMIT 1")
