# For pytest
# For the correct receipt of the token via approle
path "auth/token/lookup" {
  capabilities = ["read"]
}
# For pytest
# To revoke the token after creating and testing approle
path "auth/token/revoke" {
  capabilities = ["update"]
}
# For pytest
# To read and update the namespace configuration
path "testapp-1/config" {
  capabilities = ["read", "list", "update"]
}
# For module
# To work with secret apllication data
path "testapp-1/data/configuration/*" {
  capabilities = ["create", "read", "update", "list"]
}
# For module
# To work with secret event data
path "testapp-1/data/events/*" {
  capabilities = ["create", "read", "update", "list"]
}