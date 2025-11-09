"""Utility functions for the DAM SDK"""
import os
import mimetypes
from typing import Optional, Dict, Any
from pathlib import Path

def get_file_mimetype(file_path: str) -> str:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def validate_file_size(file_path: str, max_size: int) -> bool:
    """Validate file size against maximum limit"""
    file_size = os.path.getsize(file_path)
    return file_size <= max_size

def format_bytes(size: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe upload"""
    # Remove path components and keep only the filename
    filename = Path(filename).name
    
    # Replace or remove problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename

def build_query_params(params: Dict[str, Any]) -> str:
    """Build URL query string from parameters"""
    if not params:
        return ""
    
    query_parts = []
    for key, value in params.items():
        if value is not None:
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, tuple)):
                value = ','.join(str(v) for v in value)
            else:
                value = str(value)
            query_parts.append(f"{key}={value}")
    
    return "?" + "&".join(query_parts) if query_parts else ""

def chunked_upload(file_path: str, chunk_size: int = 8192):
    """Generator for chunked file upload"""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def is_supported_format(format_str: str) -> bool:
    """Check if image format is supported for transformations"""
    from .constants import SUPPORTED_FORMATS
    return format_str.lower() in SUPPORTED_FORMATS