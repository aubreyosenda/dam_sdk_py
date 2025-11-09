"""
Pytest configuration and fixtures for DAM SDK tests
"""

import pytest
import os
from unittest.mock import Mock, patch
from dam_sdk import DAMClient

@pytest.fixture
def mock_dam_client():
    """Fixture for mocked DAM client"""
    with patch('dam_sdk.client.requests.Session') as mock_session:
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        client = DAMClient(
            api_url='http://localhost:55055',
            key_id='test-key',
            key_secret='test-secret'
        )
        
        yield client, mock_session_instance

@pytest.fixture
def sample_file_data():
    """Fixture for sample file data"""
    return {
        'id': 'file-123',
        'filename': 'test.jpg',
        'original_name': 'test.jpg',
        'mime_type': 'image/jpeg',
        'size': 1024,
        'storage_path': 'user-123/root/test.jpg',
        'file_url': 'http://localhost:55055/api/files/serve/user-123/root/test.jpg',
        'user_id': 'user-123',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }

@pytest.fixture
def sample_files_response():
    """Fixture for sample files list response"""
    return {
        'success': True,
        'data': [
            {
                'id': 'file-1',
                'filename': 'test1.jpg',
                'original_name': 'test1.jpg',
                'mime_type': 'image/jpeg',
                'size': 1024,
                'storage_path': 'user-123/root/test1.jpg',
                'file_url': 'http://localhost:55055/api/files/serve/user-123/root/test1.jpg',
                'user_id': 'user-123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            },
            {
                'id': 'file-2',
                'filename': 'test2.png',
                'original_name': 'test2.png',
                'mime_type': 'image/png',
                'size': 2048,
                'storage_path': 'user-123/root/test2.png',
                'file_url': 'http://localhost:55055/api/files/serve/user-123/root/test2.png',
                'user_id': 'user-123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }
        ],
        'pagination': {
            'total': 2,
            'limit': 50,
            'offset': 0,
            'hasMore': False
        }
    }