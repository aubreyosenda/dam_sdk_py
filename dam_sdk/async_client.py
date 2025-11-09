"""Asynchronous DAM client"""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Union, BinaryIO
from pathlib import Path

from .client import DAMClient
from .models import File, UploadResponse, FileListResponse, UploadOptions, SearchOptions, TransformOptions
from .exceptions import DAMError, NetworkError, TimeoutError
from .utils import get_file_mimetype, validate_file_size, sanitize_filename

class AsyncDAMClient:
    """
    Asynchronous client for DAM System API
    
    Example:
        >>> import asyncio
        >>> from dam_sdk import AsyncDAMClient
        >>> 
        >>> async def main():
        ...     client = AsyncDAMClient(
        ...         api_url='http://localhost:55055',
        ...         key_id='your-key-id',
        ...         key_secret='your-key-secret'
        ...     )
        ...     file = await client.upload_file('image.jpg')
        ...     print(f"Uploaded: {file.id}")
        ... 
        >>> asyncio.run(main())
    """
    
    def __init__(
        self,
        api_url: str,
        key_id: str,
        key_secret: str,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        self.api_url = api_url.rstrip('/')
        self.key_id = key_id
        self.key_secret = key_secret
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.verify_ssl = verify_ssl
        self.session = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _ensure_session(self):
        """Ensure session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'X-API-Key-ID': self.key_id,
                    'X-API-Key-Secret': self.key_secret,
                    'User-Agent': 'DAM-Python-SDK/1.0.0',
                    'Accept': 'application/json',
                }
            )
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """Make async HTTP request"""
        await self._ensure_session()
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status != 200:
                    # Use sync client for error handling
                    sync_client = DAMClient(
                        self.api_url, self.key_id, self.key_secret
                    )
                    try:
                        # Create a mock response for error handling
                        class MockResponse:
                            def __init__(self, status_code, text, headers):
                                self.status_code = status_code
                                self.text = text
                                self.headers = headers
                            
                            def json(self):
                                import json as json_module
                                return json_module.loads(self.text)
                        
                        text = await response.text()
                        mock_response = MockResponse(
                            response.status, text, dict(response.headers)
                        )
                        sync_client._handle_response(mock_response)
                    finally:
                        sync_client.close()
                
                response_data = await response.json()
                return response_data
                
        except aiohttp.ClientTimeout as e:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds") from e
        except aiohttp.ClientConnectionError as e:
            raise NetworkError("Network connection failed") from e
        except aiohttp.ClientError as e:
            raise DAMError(f"Request failed: {str(e)}") from e
    
    async def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        options: Optional[UploadOptions] = None
    ) -> File:
        """Upload a single file asynchronously"""
        options = options or UploadOptions()
        
        await self._ensure_session()
        
        if isinstance(file_path, (str, Path)):
            file_path = str(file_path)
            if not validate_file_size(file_path, 100 * 1024 * 1024):
                from .exceptions import FileTooLargeError
                raise FileTooLargeError("File exceeds maximum size")
            
            filename = sanitize_filename(file_path)
            mime_type = get_file_mimetype(file_path)
            
            data = aiohttp.FormData()
            if options.folder_id:
                data.add_field('folder_id', options.folder_id)
            if options.metadata:
                import json
                data.add_field('metadata', json.dumps(options.metadata))
            
            with open(file_path, 'rb') as f:
                data.add_field('file', f, filename=filename, content_type=mime_type)
                
                response_data = await self._request(
                    'POST',
                    '/api/public/single',
                    data=data
                )
        else:
            # File-like object (simplified implementation)
            raise NotImplementedError("File-like objects not yet supported in async client")
        
        file_data = response_data.get('data', {})
        return File.from_dict(file_data)
    
    async def list_files(self, options: Optional[SearchOptions] = None) -> FileListResponse:
        """List files asynchronously"""
        options = options or SearchOptions()
        
        params = {
            'folder_id': options.folder_id,
            'mime_type': options.mime_type,
            'search': options.search,
            'limit': options.limit,
            'offset': options.offset,
        }
        
        response_data = await self._request('GET', '/api/public/files', params=params)
        
        files = []
        for file_data in response_data.get('data', []):
            files.append(File.from_dict(file_data))
        
        return FileListResponse(
            success=response_data.get('success', False),
            data=files,
            pagination=response_data.get('pagination', {})
        )
    
    async def get_file(self, file_id: str) -> File:
        """Get file details asynchronously"""
        endpoint = f"/api/public/files/{file_id}"
        response_data = await self._request('GET', endpoint)
        
        file_data = response_data.get('data', {})
        return File.from_dict(file_data)
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file asynchronously"""
        endpoint = f"/api/public/files/{file_id}"
        response_data = await self._request('DELETE', endpoint)
        
        return response_data.get('success', False)
    
    async def close(self):
        """Close the async session"""
        if self.session:
            await self.session.close()
            self.session = None