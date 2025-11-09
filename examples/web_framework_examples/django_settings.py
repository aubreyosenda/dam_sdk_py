"""
Django settings configuration for DAM SDK integration
"""

# settings.py - Add these configurations

# DAM Configuration
DAM_CONFIG = {
    'API_URL': 'https://your-dam-server.com',  # Your DAM server URL
    'KEY_ID': 'your-production-key-id',        # Production API key ID
    'KEY_SECRET': 'your-production-key-secret', # Production API key secret
    'TIMEOUT': 30,                             # Request timeout in seconds
    'MAX_RETRIES': 3,                          # Maximum retry attempts
}

# For development vs production environments
import os
if os.getenv('DJANGO_ENV') == 'development':
    DAM_CONFIG.update({
        'API_URL': 'http://localhost:55055',
        'KEY_ID': os.getenv('DAM_DEV_KEY_ID', 'dev-key-id'),
        'KEY_SECRET': os.getenv('DAM_DEV_KEY_SECRET', 'dev-key-secret'),
    })
elif os.getenv('DJANGO_ENV') == 'staging':
    DAM_CONFIG.update({
        'API_URL': 'https://staging-dam.yourcompany.com',
        'KEY_ID': os.getenv('DAM_STAGING_KEY_ID'),
        'KEY_SECRET': os.getenv('DAM_STAGING_KEY_SECRET'),
    })

# Optional: Django Storage Backend for DAM
"""
# Add to settings.py if you want to use DAM as a storage backend
STORAGES = {
    "default": {
        "BACKEND": "your_app.storage.DAMStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
"""

# Optional: File upload settings
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_FILE_TYPES = [
    'image/jpeg',
    'image/png', 
    'image/gif',
    'image/webp',
    'application/pdf',
    'video/mp4',
]

# Optional: Cache configuration for DAM URLs
CACHES = {
    'dam_urls': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 3600,  # 1 hour
    }
}