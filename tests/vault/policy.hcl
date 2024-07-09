
# Operations for pytest
# Allow read access to retrieve the token using approle
path "auth/token/lookup" {
  capabilities = ["read"]
}

# Operations for pytest
# Allow updating capabilities for token revocation after creating and testing approle
path "auth/token/revoke" {
  capabilities = ["update"]
}

# Operations for the module
# Enable read access for self-lookup with tokens
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Operations for pytest
# Allow read, create or update operations on the pytest path
path "sys/mounts/pytests" {
  capabilities = ["read", "create", "update"]
}

# Operations for the module
# Read and update namespace configuration
path "pytests/config" {
  capabilities = ["read", "list", "update"]
}

# Operations for the module
# Work with secret application data
path "pytests/data/configuration/*" {
  capabilities = ["create", "read", "update", "list"]
}

# To work with database engine
path "database/creds/*" {
  capabilities = ["create", "read", "update", "list", "delete"]
}
