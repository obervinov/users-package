"""
This test is necessary to verify permissions on the provided user ID.
"""
from unittest.mock import Mock
from users.users import UsersAuth

mock_vault = Mock()
users_auth = UsersAuth(mock_vault)

permissions_mapping = {
    123456: 'allow',
    654321: 'deny'
}


def test_check_permissions():
    """
    The function checks whether the method of verifying the rights
    of the user ID is working correctly when responding from Vault - `allow` or `deny`.
    """
    for userid, permissions in permissions_mapping.items():
        mock_vault.vault_read_secrets.return_value = permissions
        assert users_auth.check_permissions(userid) == permissions



if __name__ == "__main__":
    test_check_permissions()
    print("Test with check_permissions - passed")
