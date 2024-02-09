"""
Custom exceptions for the Users package.
"""


class WrongUserConfiguration(Exception):
    """
    Raised when the configuration for a user is incorrect.

    Args:
        message (str): The error message.

    Example:
        >>> try:
        ...     raise WrongUserConfiguration("Incorrect user configuration")
        ... except WrongUserConfiguration as e:
        ...     print(e)
        Incorrect user configuration
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class VaultInstanceNotSet(Exception):
    """
    Raised when the Vault instance is not set.

    Args:
        message (str): The error message.

    Example:
        >>> try:
        ...     raise VaultInstanceNotSet("Vault instance not set")
        ... except VaultInstanceNotSet as e:
        ...     print(e)
        Vault instance not set
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)
