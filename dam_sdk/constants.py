"""Constants and configuration for the DAM SDK"""

# Default configuration
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_CHUNK_SIZE = 8192

# File upload limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_BATCH_FILES = 10

# Supported file formats for transformations
SUPPORTED_FORMATS = {
    'jpeg', 'jpg', 'png', 'webp', 'avif', 'gif'
}

# Transformation options
TRANSFORM_FIT_OPTIONS = {
    'cover', 'contain', 'fill', 'inside', 'outside'
}

# API endpoints
ENDPOINTS = {
    'upload_single': '/api/public/single',
    'upload_multiple': '/api/public/multiple',
    'files_list': '/api/public/files',
    'file_detail': '/api/public/files/{id}',
    'file_delete': '/api/public/files/{id}',
    'transform': '/api/transform/{id}',
    'thumbnail': '/api/transform/{id}/thumbnail',
    'stats_dashboard': '/api/stats/dashboard',
    'stats_storage': '/api/stats/storage',
}

# HTTP headers
HEADERS = {
    'User-Agent': 'DAM-Python-SDK/1.0.0',
    'Accept': 'application/json',
}

# Retry configuration
RETRY_STATUS_CODES = {408, 429, 500, 502, 503, 504}
RETRY_METHODS = {'GET', 'POST', 'PUT', 'DELETE'}