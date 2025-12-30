# Copilot Instructions for users-package

## Project Overview
A production-grade Python package providing **user management for Telegram bots**: authentication, authorization, and rate limiting. Distributed as a Poetry-managed package installed via Git tags (e.g., `v4.1.3`).

## Architecture & Component Boundaries

### Three-Layer Design
1. **[users/users.py](../users/users.py)** - Orchestrates auth/authz flows, exposes `@access_control` decorator and `user_access_check()` entrypoint
2. **[users/storage.py](../users/storage.py)** - PostgreSQL client for user metadata (`users` table) and request logging (`users_requests` table)
3. **[users/ratelimiter.py](../users/ratelimiter.py)** - Calculates request counters (hourly/daily) and validates limits

### External Dependencies
- **Vault (HashiCorp)** - Stores all configuration at `configuration/users/{user_id}` (access control, roles, rate limits)
- **PostgreSQL** - Persists user status and request history (schema: [tests/postgres/tables.sql](../tests/postgres/tables.sql))
- Custom packages: `logger` (logging), `vault` (Vault API client)

### Initialization Patterns
Users class accepts **two credential modes**:
```python
# Mode 1: Direct connection (simpler, static credentials)
Users(vault=<VaultClient>, storage_connection=psycopg2.connect(...))

# Mode 2: Vault Database Engine (dynamic credentials)
Users(vault={'instance': <VaultClient>, 'role': 'my-dbengine-role'})
```

## Critical Workflows

### Running Tests
```bash
# Start dependencies
docker-compose up -d

# Run ordered tests (MUST be sequential due to data dependencies)
pytest --verbose -s tests/

# Tests use @pytest.mark.order(N) for execution order
```
**Key fixtures** (in [tests/conftest.py](../tests/conftest.py)):
- `vault_instance` - Pre-configured Vault with test users
- `postgres_instance` - PostgreSQL with initialized tables
- Test users: `testUser1` (admin), `testUser2` (financial+goals), `testUser20` (denied)

### Local Development
```bash
poetry install       # Install dependencies
poetry shell         # Activate virtualenv
pytest tests/        # Run tests
```

### Linting & Code Quality
- **Flake8**: Max line length 170 (see [.flake8](../.flake8))
- **Pylint**: Standard config in [.pylintrc](../.pylintrc)
- **CI**: GitHub Actions runs both on PR ([.github/workflows/pr.yaml](workflows/pr.yaml))

## Project-Specific Conventions

### Naming Standards
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `USER_STATUS_ALLOW`, `USERS_VAULT_CONFIG_PATH`)
- **Database tables/columns**: `snake_case` (e.g., `users_requests`, `message_id`)
- **Python methods/vars**: `snake_case` as per PEP8
- **Configuration keys**: `snake_case` (e.g., `requests_per_day`, `random_shift_minutes`)

### Error Handling Patterns
- **Custom exceptions** in [users/exceptions.py](../users/exceptions.py):
  - `VaultInstanceNotSet` - Missing/invalid Vault instance
  - `FailedStorageConnection` - PostgreSQL connection failure
  - `WrongUserConfiguration` - Malformed Vault config for user
  - `FailedDeterminateRateLimit` - Rate limit calculation error
  
- **Auto-reconnect decorator** in Storage class:
  ```python
  @reconnect_on_exception  # Catches psycopg2.Error, attempts reconnect
  def log_user_request(self, ...):
  ```

### Vault Configuration Structure
User config stored at `configuration/users/{user_id}`:
```json
{
  "status": "allowed",
  "roles": ["admin_role", "financial_role"],
  "requests": {
    "requests_per_day": 10,
    "requests_per_hour": 5,
    "random_shift_minutes": 30
  }
}
```

### Response Structure
`user_access_check()` returns standardized dict:
```python
{
  'access': 'allowed' | 'denied',           # Authentication status
  'permissions': 'allowed' | 'denied',      # Authorization (if role_id provided)
  'rate_limits': datetime | None            # When limits expire (if enabled)
}
```

## Integration Points

### Telegram Bot Integration
Use `@access_control` decorator on message handlers:
```python
@bot.message_handler(commands=['admin'])
@access_control(role_id='admin_role', flow='authz')
def admin_command(message, access_result: dict = None):
    # access_result contains {'access', 'permissions', 'rate_limits'}
    if access_result['permissions'] == 'denied':
        bot.reply_to(message, "Access denied")
```

### Database Schema
**Key tables** (see [tests/postgres/tables.sql](../tests/postgres/tables.sql)):
- `users`: `user_id`, `chat_id`, `status`
- `users_requests`: `user_id`, `message_id`, `authentication`, `authorization`, `timestamp`, `rate_limits`

## Development Guidelines

### Adding New Features
1. Update relevant class in `users/` module
2. Add corresponding test in `tests/test_*.py` with `@pytest.mark.order(N)`
3. Update [README.md](../README.md) with usage examples
4. Update [CHANGELOG.md](../CHANGELOG.md) following Keep a Changelog format

### Versioning & Release
- Follows **Semantic Versioning** (current: `v4.1.3`)
- Update `pyproject.toml` version and `CHANGELOG.md`
- Create Git tag: `git tag v4.x.x && git push --tags`
- Package consumed via: `users = { git = "https://github.com/obervinov/users-package.git", tag = "v4.x.x" }`

### Test Coverage Requirements
All core functionality MUST have tests:
- Authentication logic: [tests/test_users_access.py](../tests/test_users_access.py)
- Authorization logic: Same file, role-based tests
- Rate limiting: [tests/test_rate_limits.py](../tests/test_rate_limits.py)
- Storage operations: [tests/test_dbengine.py](../tests/test_dbengine.py)
- Decorators: [tests/test_decorators.py](../tests/test_decorators.py)

## Common Pitfalls

### Test Execution Order
❌ **Don't** run tests in random order - data dependencies exist  
✅ **Do** use `@pytest.mark.order(N)` and run sequentially

### Vault Configuration
❌ **Don't** assume configuration exists - handle `None` gracefully  
✅ **Do** validate config in `__init__` with `WrongUserConfiguration`

### Database Connections
❌ **Don't** ignore `psycopg2.Error` exceptions  
✅ **Do** use `@reconnect_on_exception` for resilience

### Rate Limit Logic
❌ **Don't** modify rate limit logic without updating tests  
✅ **Do** test both `requests_per_hour` and `requests_per_day` scenarios

## Token Authentication (Planned v4.2.0)

### Feature Overview
Adding generic token-based authentication for frontend integration (web UIs, mobile apps, CLI tools). Tokens provide temporary access without storing user credentials.

### Token Format & Generation
```python
# Token format: "user_id.token_id"
# Example: "123456.a8f3kjs9dfjkl23jrlksjdf..."
token_id = secrets.token_urlsafe(32)  # ~43 chars
token = f"{user_id}.{token_id}"       # Total ~45-50 chars
```

### Security Implementation
**Hashing with PBKDF2**:
```python
import hashlib
import secrets

# Generate & store
salt = secrets.token_hex(32)
token_hash = hashlib.pbkdf2_hmac('sha256', token_id.encode(), salt.encode(), 100_000).hex()

# Validate
computed_hash = hashlib.pbkdf2_hmac('sha256', provided_token.encode(), stored_salt.encode(), 100_000).hex()
valid = secrets.compare_digest(computed_hash, stored_hash)
```

### Database Schema
New `users_tokens` table (add to [tests/postgres/tables.sql](../tests/postgres/tables.sql)):
```sql
CREATE TABLE users_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    token_hash VARCHAR(128) NOT NULL,
    token_salt VARCHAR(64) NOT NULL,
    token_expires_at TIMESTAMP NOT NULL,
    token_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_tokens_user_id ON users_tokens(user_id);
```

### Planned Method Signatures

**Storage class** ([users/storage.py](../users/storage.py)):
```python
def store_token(self, user_id: str, token_hash: str, token_salt: str, expires_at: datetime) -> None:
    """Store hashed token. Marks previous active tokens as used."""

def get_token(self, user_id: str) -> Optional[dict]:
    """Retrieve most recent unused, non-expired token for user."""

def mark_token_used(self, user_id: str) -> None:
    """Mark user's active token as used (single-use enforcement)."""
```

**Users class** ([users/users.py](../users/users.py)):
```python
def issue_token(self, user_id: str, ttl_minutes: int = 10) -> str:
    """Generate temporary access token. Returns plaintext token string."""

def validate_token(self, token: str) -> Optional[dict]:
    """Validate token, return user info or None. Marks token as used."""

def revoke_token(self, user_id: str) -> None:
    """Revoke existing token for user."""
```

### Token Lifecycle
1. **Issue**: Bot calls `issue_token()` → generates hash/salt → stores in DB → returns plaintext token
2. **Validate**: Frontend calls `validate_token()` → fetches from DB → verifies hash/expiry/used → returns user data
3. **Single-use**: After validation, marks `token_used=True`
4. **Revoke**: New token issuance auto-revokes previous tokens

### Integration Example
**Database Bridge Pattern** (e.g., pyinstabot-downloader):
- Telegram bot calls `users.issue_token(user_id)` to generate token
- Web frontend calls `users.validate_token(token)` to authenticate
- Both access same PostgreSQL `users_tokens` table
- No direct bot ↔ frontend communication needed

### Implementation Checklist
- [ ] Add `users_tokens` table to [tests/postgres/tables.sql](../tests/postgres/tables.sql)
- [ ] Implement `Storage.store_token()`, `Storage.get_token()`, `Storage.mark_token_used()`
- [ ] Implement `Users.issue_token()`, `Users.validate_token()`, `Users.revoke_token()`
- [ ] Add backward compatibility checks (gracefully handle missing table)
- [ ] Write tests in `tests/test_tokens.py` with `@pytest.mark.order(N)`
- [ ] Update [README.md](../README.md) with token usage examples
- [ ] Update [CHANGELOG.md](../CHANGELOG.md) with v4.2.0 entry
- [ ] Bump version in [pyproject.toml](../pyproject.toml) to `4.2.0`
- [ ] Add new exceptions to `__all__` in [users/__init__.py](../users/__init__.py)
