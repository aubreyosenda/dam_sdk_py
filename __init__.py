"""
DAM Python SDK
Official Python client library for DAM System API

Author: Aubrey Osenda
Version: 1.0.0
License: MIT

Example:
    >>> from dam_sdk import DAMClient
    >>> 
    >>> client = DAMClient(
    ...     api_url='http://localhost:55055',
    ...     key_id='your-key-id',
    ...     key_secret='your-key-secret'
    ... )
    >>> 
    >>> # Upload a file
    >>> with open('image.jpg', 'rb') as f:
    ...     file = client.upload(f, folder_id='my-folder')
    >>> 
    >>> print(f"Uploaded: {file['id']}")
"""

from .client import DAMClient
from .async_client import AsyncDAMClient
from .models import (
    File, Folder, UploadResponse, FileListResponse,
    TransformOptions, UploadOptions, SearchOptions
)
from .exceptions import (
    DAMError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    FileTooLargeError,
    NetworkError,
    TimeoutError,
    ServerError
)
from .constants import SUPPORTED_FORMATS, MAX_FILE_SIZE

__version__ = "1.0.0"
__author__ = "Aubrey Osenda"
__license__ = "MIT"

__all__ = [
    # Main clients
    "DAMClient",
    "AsyncDAMClient",
    
    # Models
    "File",
    "Folder", 
    "UploadResponse",
    "FileListResponse",
    "TransformOptions",
    "UploadOptions",
    "SearchOptions",
    
    # Exceptions
    "DAMError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError", 
    "ValidationError",
    "RateLimitError",
    "FileTooLargeError",
    "NetworkError",
    "TimeoutError",
    "ServerError",
    
    # Constants
    "SUPPORTED_FORMATS",
    "MAX_FILE_SIZE",
    
    # Metadata
    "__version__",
    "__author__", 
    "__license__",
]