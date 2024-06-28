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


class StorageInstanceNotSet(Exception):
    """
    Raised when the storage instance is not set.

    Args:
        message (str): The error message.

    Example:
        >>> try:
        ...     raise StorageInstanceNotSet("Storage instance not set")
        ... except StorageInstanceNotSet as e:
        ...     print(e)
        Storage instance not set
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class FailedDeterminateRateLimit(Exception):
    """
    Raised when the rate limit cannot be determinated.

    Args:
        message (str): The error message.

    Example:
        >>> try:
        ...     raise FaildDeterminateRateLimit("Failed to determinate rate limit")
        ... except FaildDeterminateRateLimit as e:
        ...     print(e)
        Failed to determinate rate limit
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class FailedStorageConnection(Exception):
    """
    Raised when the storage connection fails.

    Args:
        message (str): The error message.

    Example:
        >>> try:
        ...     raise FailedStorageConnection("Failed to connect to storage")
        ... except FailedStorageConnection as e:
        ...     print(e)
        Failed to connect to storage
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)
