"""
Tests for AsyncDAMClient
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sdks.python.dam_sdk_py.dam_sdk._init_ import AsyncDAMClient, DAMError

class TestAsyncDAMClient:
    
    @pytest.mark.asyncio
    async def test_async_client_initialization(self):
        """Test async client initialization"""
        async with AsyncDAMClient(
            api_url='http://localhost:55055',
            key_id='test-key',
            key_secret='test-secret'
        ) as client:
            assert client.api_url == 'http://localhost:55055'
            assert client.key_id == 'test-key'
            assert client.key_secret == 'test-secret'
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager"""
        async with AsyncDAMClient(
            api_url='http://localhost:55055',
            key_id='test-key',
            key_secret='test-secret'
        ) as client:
            assert client.session is not None
        
        # Session should be closed after context manager
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_async_list_files(self, sample_files_response):
        """Test async list files"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = sample_files_response
            mock_session_instance.request.return_value.__aenter__.return_value = mock_response
            
            async with AsyncDAMClient(
                api_url='http://localhost:55055',
                key_id='test-key',
                key_secret='test-secret'
            ) as client:
                result = await client.list_files()
                
                assert result.success is True
                assert len(result.data) == 2
                assert result.data[0].id == 'file-1'
                assert result.data[1].id == 'file-2'
    
    @pytest.mark.asyncio
    async def test_async_get_file(self, sample_file_data):
        """Test async get file"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'success': True,
                'data': sample_file_data
            }
            mock_session_instance.request.return_value.__aenter__.return_value = mock_response
            
            async with AsyncDAMClient(
                api_url='http://localhost:55055',
                key_id='test-key',
                key_secret='test-secret'
            ) as client:
                file = await client.get_file('file-123')
                
                assert file.id == 'file-123'
                assert file.original_name == 'test.jpg'
                assert file.mime_type == 'image/jpeg'
    
    @pytest.mark.asyncio
    async def test_async_delete_file(self):
        """Test async delete file"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'success': True,
                'message': 'File deleted successfully'
            }
            mock_session_instance.request.return_value.__aenter__.return_value = mock_response
            
            async with AsyncDAMClient(
                api_url='http://localhost:55055',
                key_id='test-key',
                key_secret='test-secret'
            ) as client:
                success = await client.delete_file('file-123')
                
                assert success is True
    
    @pytest.mark.asyncio
    async def test_async_request_timeout(self):
        """Test async request timeout"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            mock_session_instance.request.side_effect = asyncio.TimeoutError("Request timed out")
            
            async with AsyncDAMClient(
                api_url='http://localhost:55055',
                key_id='test-key',
                key_secret='test-secret'
            ) as client:
                with pytest.raises(Exception) as exc_info:
                    await client.list_files()
                
                assert "Request timed out" in str(exc_info.value)