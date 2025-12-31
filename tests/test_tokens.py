"""
A test that checks the token authentication functionality.
"""
import time
import pytest


@pytest.mark.order(18)
def test_issue_token_success(users_instance):
    """
    Verify successful token issuance for a valid user.
    """
    token = users_instance.issue_token(user_id='testUser1', ttl_minutes=10)

    # Verify token format
    assert token is not None
    assert '.' in token
    assert token.startswith('testUser1.')

    # Verify token components
    parts = token.split('.', 1)
    assert len(parts) == 2
    assert parts[0] == 'testUser1'
    assert len(parts[1]) > 40  # token_urlsafe(32) generates ~43 chars


@pytest.mark.order(19)
def test_issue_token_without_user_id(users_instance):
    """
    Verify that token issuance fails without user_id.
    """
    with pytest.raises(ValueError, match="user_id is required for token issuance"):
        users_instance.issue_token(user_id=None)


@pytest.mark.order(20)
def test_validate_token_success(users_instance):
    """
    Verify successful token validation for a valid token.
    """
    # Issue a token
    token = users_instance.issue_token(user_id='testUser1', ttl_minutes=10)

    # Validate the token
    user_info = users_instance.validate_token(token=token)

    # Verify user information
    assert user_info is not None
    assert user_info['user_id'] == 'testUser1'
    assert user_info['status'] == users_instance.user_status_allow
    assert 'admin_role' in user_info['roles']


@pytest.mark.order(21)
def test_validate_token_single_use(users_instance):
    """
    Verify that tokens can only be used once (single-use enforcement).
    """
    # Issue a token
    token = users_instance.issue_token(user_id='testUser2', ttl_minutes=10)

    # First validation should succeed
    user_info_first = users_instance.validate_token(token=token)
    assert user_info_first is not None
    assert user_info_first['user_id'] == 'testUser2'

    # Second validation should fail (token already used)
    user_info_second = users_instance.validate_token(token=token)
    assert user_info_second is None


@pytest.mark.order(22)
def test_validate_token_invalid_format(users_instance):
    """
    Verify that validation fails with invalid token format.
    """
    with pytest.raises(ValueError, match="Invalid token format"):
        users_instance.validate_token(token='invalid_token')

    with pytest.raises(ValueError, match="Invalid token format"):
        users_instance.validate_token(token=None)


@pytest.mark.order(23)
def test_validate_token_wrong_hash(users_instance):
    """
    Verify that validation fails with wrong token hash.
    """
    # Issue a token
    token = users_instance.issue_token(user_id='testUser3', ttl_minutes=10)

    # Tamper with the token
    parts = token.split('.', 1)
    tampered_token = f"{parts[0]}.tampered_hash_value_123456789"

    # Validation should fail
    user_info = users_instance.validate_token(token=tampered_token)
    assert user_info is None


@pytest.mark.order(24)
def test_validate_token_expired(users_instance):
    """
    Verify that validation fails for expired tokens.
    """
    # Issue a token with very short TTL
    token = users_instance.issue_token(user_id='testUser4', ttl_minutes=0.01)

    # Wait for token to expire
    time.sleep(2)

    # Validation should fail
    user_info = users_instance.validate_token(token=token)
    assert user_info is None


@pytest.mark.order(25)
def test_validate_token_nonexistent_user(users_instance):
    """
    Verify token validation for a user that doesn't exist.
    """
    # Create a fake token for non-existent user
    fake_token = "testUser999.fake_token_id_12345678901234567890"

    # Validation should fail
    user_info = users_instance.validate_token(token=fake_token)
    assert user_info is None


@pytest.mark.order(26)
def test_revoke_token_success(users_instance):
    """
    Verify successful token revocation.
    """
    # Issue a token
    token = users_instance.issue_token(user_id='testUser5', ttl_minutes=10)

    # Revoke the token
    users_instance.revoke_token(user_id='testUser5')

    # Validation should fail after revocation
    user_info = users_instance.validate_token(token=token)
    assert user_info is None


@pytest.mark.order(27)
def test_revoke_token_without_user_id(users_instance):
    """
    Verify that token revocation fails without user_id.
    """
    with pytest.raises(ValueError, match="user_id is required for token revocation"):
        users_instance.revoke_token(user_id=None)


@pytest.mark.order(28)
def test_multiple_tokens_auto_revoke(users_instance):
    """
    Verify that issuing a new token automatically revokes previous tokens.
    """
    # Issue first token
    token1 = users_instance.issue_token(user_id='testUser6', ttl_minutes=10)

    # Issue second token (should revoke first)
    token2 = users_instance.issue_token(user_id='testUser6', ttl_minutes=10)

    # First token should be invalid
    user_info1 = users_instance.validate_token(token=token1)
    assert user_info1 is None

    # Second token should be valid
    user_info2 = users_instance.validate_token(token=token2)
    assert user_info2 is not None
    assert user_info2['user_id'] == 'testUser6'


@pytest.mark.order(29)
def test_token_with_denied_user(users_instance):
    """
    Verify token functionality with a denied user.
    """
    # Issue token for denied user
    token = users_instance.issue_token(user_id='testUser20', ttl_minutes=10)

    # Validate token
    user_info = users_instance.validate_token(token=token)

    # Token should validate but user should be denied
    assert user_info is not None
    assert user_info['user_id'] == 'testUser20'
    assert user_info['status'] == users_instance.user_status_deny


@pytest.mark.order(30)
def test_token_backward_compatibility(users_instance_without_rl, postgres_instance):
    """
    Verify backward compatibility when users_tokens table doesn't exist.
    """
    cursor = postgres_instance[1]
    connection = postgres_instance[0]

    # Temporarily drop the users_tokens table
    cursor.execute("DROP TABLE IF EXISTS users_tokens CASCADE")
    connection.commit()

    # Try to issue token (should not raise exception, returns None when storage unavailable)
    token = users_instance_without_rl.issue_token(user_id='testUser7', ttl_minutes=10)

    # Token should be None to signal storage unavailability
    assert token is None

    # Recreate the table for subsequent tests
    cursor.execute("""
        CREATE TABLE users_tokens (
            id serial PRIMARY KEY,
            user_id VARCHAR (255) NOT NULL,
            token_hash VARCHAR (128) NOT NULL,
            token_salt VARCHAR (64) NOT NULL,
            token_expires_at TIMESTAMP NOT NULL,
            token_used BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX idx_users_tokens_user_id ON users_tokens(user_id)")
    connection.commit()


@pytest.mark.order(31)
def test_token_storage_in_database(users_instance, postgres_instance):
    """
    Verify that tokens are properly stored in the database.
    """
    cursor = postgres_instance[1]

    # Issue a token
    _ = users_instance.issue_token(user_id='testUser8', ttl_minutes=10)

    # Check database for the token
    cursor.execute("SELECT user_id, token_used FROM users_tokens WHERE user_id = 'testUser8' ORDER BY created_at DESC LIMIT 1")
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == 'testUser8'
    assert result[1] is False  # token_used should be False


@pytest.mark.order(32)
def test_token_with_custom_ttl(users_instance):
    """
    Verify token issuance with custom TTL.
    """
    # Issue tokens with different TTLs
    token_short = users_instance.issue_token(user_id='testUser9', ttl_minutes=1)
    token_long = users_instance.issue_token(user_id='testUser10', ttl_minutes=60)

    # Both tokens should be valid
    assert token_short is not None
    assert token_long is not None

    # Validate short TTL token
    user_info_short = users_instance.validate_token(token=token_short)
    assert user_info_short is not None

    # Different user with a longer TTL; short token was for testUser9 and is now used
    # Validate long TTL token
    user_info_long = users_instance.validate_token(token=token_long)
    assert user_info_long is not None
