"""Custom exceptions for the DAM SDK"""

class DAMError(Exception):
    """Base exception for all DAM SDK errors"""
    pass

class AuthenticationError(DAMError):
    """Authentication failed - invalid API credentials"""
    pass

class AuthorizationError(DAMError):
    """Insufficient permissions for the requested operation"""
    pass

class NotFoundError(DAMError):
    """Requested resource was not found"""
    pass

class ValidationError(DAMError):
    """Invalid input data or parameters"""
    pass

class RateLimitError(DAMError):
    """Rate limit exceeded"""
    pass

class FileTooLargeError(DAMError):
    """File size exceeds maximum allowed limit"""
    pass

class NetworkError(DAMError):
    """Network connectivity issue"""
    pass

class TimeoutError(DAMError):
    """Request timed out"""
    pass

class ServerError(DAMError):
    """Server returned an error response"""
    
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class ConfigurationError(DAMError):
    """Invalid SDK configuration"""
    pass