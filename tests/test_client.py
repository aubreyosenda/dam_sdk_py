import pytest
import os
from unittest.mock import Mock, patch
from sdks.python.dam_sdk_py.dam_sdk._init_ import DAMClient, AuthenticationError, ValidationError

class TestDAMClient:
    
    def test_client_initialization(self):
        """Test client initialization with required parameters"""
        client = DAMClient(
            api_url='http://localhost:55055',
            key_id='test-key',
            key_secret='test-secret'
        )
        
        assert client.api_url == 'http://localhost:55055'
        assert client.key_id == 'test-key'
        assert client.key_secret == 'test-secret'
        assert client.timeout == 30
    
    def test_client_with_custom_timeout(self):
        """Test client with custom timeout"""
        client = DAMClient(
            api_url='http://localhost:55055',
            key_id='test-key',
            key_secret='test-secret',
            timeout=60
        )
        
        assert client.timeout == 60
    
    @patch('dam_sdk.client.requests.Session')
    def test_authentication_headers(self, mock_session):
        """Test that authentication headers are set correctly"""
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        client = DAMClient(
            api_url='http://localhost:55055',
            key_id='test-key-id',
            key_secret='test-secret'
        )
        
        # Check that headers were updated
        expected_headers = {
            'X-API-Key-ID': 'test-key-id',
            'X-API-Key-Secret': 'test-secret',
        }
        
        # Verify headers were set on session
        for key, value in expected_headers.items():
            assert mock_session_instance.headers[key] == value
    
    def test_build_query_params(self):
        """Test query parameter building"""
        from dam_sdk.utils import build_query_params
        
        params = {
            'limit': 10,
            'offset': 0,
            'search': 'test',
            'folder_id': None  # Should be excluded
        }
        
        result = build_query_params(params)
        assert 'limit=10' in result
        assert 'offset=0' in result
        assert 'search=test' in result
        assert 'folder_id' not in result
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        from dam_sdk.utils import sanitize_filename
        
        # Test with path
        assert sanitize_filename('/path/to/file.jpg') == 'file.jpg'
        
        # Test with problematic characters
        assert sanitize_filename('file<>.jpg') == 'file__.jpg'
        assert sanitize_filename('file:".jpg') == 'file__.jpg'