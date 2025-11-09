"""Main synchronous DAM client"""
import json
import time
from typing import Dict, List, Optional, Union, BinaryIO, Iterator
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import (
    File, Folder, UploadResponse, FileListResponse,
    TransformOptions, UploadOptions, SearchOptions
)
from .exceptions import (
    DAMError, AuthenticationError, AuthorizationError,
    NotFoundError, ValidationError, RateLimitError,
    FileTooLargeError, NetworkError, TimeoutError, ServerError
)
from .constants import (
    ENDPOINTS, HEADERS, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES,
    MAX_FILE_SIZE, RETRY_STATUS_CODES, RETRY_METHODS
)
from .utils import get_file_mimetype, validate_file_size, sanitize_filename, build_query_params

class DAMClient:
    """
    Synchronous client for DAM System API
    
    Example:
        >>> client = DAMClient(
        ...     api_url='http://localhost:55055',
        ...     key_id='your-key-id', 
        ...     key_secret='your-key-secret'
        ... )
        >>> 
        >>> # Upload a file
        >>> file = client.upload_file('image.jpg')
        >>> print(f"Uploaded: {file.id}")
    """
    
    def __init__(
        self,
        api_url: str,
        key_id: str,
        key_secret: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        verify_ssl: bool = True
    ):
        """
        Initialize DAM client
        
        Args:
            api_url: Base URL of DAM API (e.g., 'http://localhost:55055')
            key_id: API key ID
            key_secret: API key secret
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            verify_ssl: Verify SSL certificates
        """
        self.api_url = api_url.rstrip('/')
        self.key_id = key_id
        self.key_secret = key_secret
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Create session with retry strategy
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.headers.update({
            'X-API-Key-ID': key_id,
            'X-API-Key-Secret': key_secret,
        })
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=list(RETRY_STATUS_CODES),
            allowed_methods=RETRY_METHODS,
            backoff_factor=0.5,
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        stream: bool = False
    ) -> Dict:
        """Make HTTP request to DAM API"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                json=json_data,
                timeout=self.timeout,
                verify=self.verify_ssl,
                stream=stream
            )
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds") from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError("Network connection failed") from e
        except requests.exceptions.RequestException as e:
            raise DAMError(f"Request failed: {str(e)}") from e
        
        return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and raise appropriate exceptions"""
        try:
            response_data = response.json()
        except ValueError:
            response_data = {'message': response.text or 'Unknown error'}
        
        if response.status_code == 200:
            return response_data
        
        # Handle specific error cases
        error_message = response_data.get('message') or response_data.get('error') or 'Unknown error'
        
        if response.status_code == 401:
            raise AuthenticationError(error_message)
        elif response.status_code == 403:
            raise AuthorizationError(error_message)
        elif response.status_code == 404:
            raise NotFoundError(error_message)
        elif response.status_code == 413:
            raise FileTooLargeError(error_message)
        elif response.status_code == 422:
            raise ValidationError(error_message)
        elif response.status_code == 429:
            raise RateLimitError(error_message)
        elif 500 <= response.status_code < 600:
            raise ServerError(
                f"Server error {response.status_code}: {error_message}",
                status_code=response.status_code,
                response_data=response_data
            )
        else:
            raise DAMError(f"API error {response.status_code}: {error_message}")
    
    # FILE UPLOAD METHODS
    
    def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        options: Optional[UploadOptions] = None
    ) -> File:
        """
        Upload a single file
        
        Args:
            file_path: Path to file or file-like object
            options: Upload options (folder_id, metadata, etc.)
            
        Returns:
            File object with upload details
            
        Raises:
            FileTooLargeError: If file exceeds size limit
            ValidationError: If file type is invalid
            DAMError: For other upload errors
        """
        options = options or UploadOptions()
        
        # Handle file path or file object
        if isinstance(file_path, (str, Path)):
            file_path = str(file_path)
            if not validate_file_size(file_path, MAX_FILE_SIZE):
                raise FileTooLargeError(f"File exceeds maximum size of {MAX_FILE_SIZE} bytes")
            
            filename = sanitize_filename(file_path)
            mime_type = get_file_mimetype(file_path)
            
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, mime_type)}
                return self._upload_files(files, options)
        else:
            # File-like object
            files = {'file': ('uploaded_file', file_path, 'application/octet-stream')}
            return self._upload_files(files, options)
    
    def upload_multiple_files(
        self,
        file_paths: List[Union[str, Path, BinaryIO]],
        options: Optional[UploadOptions] = None
    ) -> UploadResponse:
        """
        Upload multiple files in a single request
        
        Args:
            file_paths: List of file paths or file-like objects
            options: Upload options
            
        Returns:
            UploadResponse with success/failure details
        """
        options = options or UploadOptions()
        
        files = []
        for i, file_path in enumerate(file_paths):
            if isinstance(file_path, (str, Path)):
                file_path = str(file_path)
                if not validate_file_size(file_path, MAX_FILE_SIZE):
                    raise FileTooLargeError(f"File {file_path} exceeds maximum size")
                
                filename = sanitize_filename(file_path)
                mime_type = get_file_mimetype(file_path)
                
                files.append(('files', (filename, open(file_path, 'rb'), mime_type)))
            else:
                files.append(('files', (f'file_{i}', file_path, 'application/octet-stream')))
        
        try:
            response_data = self._request(
                'POST',
                ENDPOINTS['upload_multiple'],
                files=files,
                data=self._build_upload_data(options)
            )
            
            # Convert response to UploadResponse
            uploaded_files = []
            if 'data' in response_data and 'uploaded' in response_data['data']:
                for file_data in response_data['data']['uploaded']:
                    uploaded_files.append(File.from_dict(file_data))
            
            return UploadResponse(
                success=response_data.get('success', False),
                message=response_data.get('message', ''),
                data=uploaded_files,
                failed=response_data.get('data', {}).get('failed', []),
                counts=response_data.get('data', {}).get('counts', {})
            )
        finally:
            # Close opened files
            for _, file_tuple in files:
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
    
    def _upload_files(self, files: Dict, options: UploadOptions) -> File:
        """Internal method to handle file upload"""
        response_data = self._request(
            'POST',
            ENDPOINTS['upload_single'],
            files=files,
            data=self._build_upload_data(options)
        )
        
        file_data = response_data.get('data', {})
        return File.from_dict(file_data)
    
    def _build_upload_data(self, options: UploadOptions) -> Dict:
        """Build form data for upload requests"""
        data = {}
        if options.folder_id:
            data['folder_id'] = options.folder_id
        if options.metadata:
            data['metadata'] = json.dumps(options.metadata)
        if options.original_name:
            data['original_name'] = options.original_name
        return data
    
    # FILE MANAGEMENT METHODS
    
    def list_files(self, options: Optional[SearchOptions] = None) -> FileListResponse:
        """
        List files with optional filtering and pagination
        
        Args:
            options: Search and filter options
            
        Returns:
            FileListResponse with files and pagination info
        """
        options = options or SearchOptions()
        
        params = {
            'folder_id': options.folder_id,
            'mime_type': options.mime_type,
            'search': options.search,
            'limit': options.limit,
            'offset': options.offset,
            'sort': options.sort,
            'order': options.order,
        }
        
        response_data = self._request('GET', ENDPOINTS['files_list'], params=params)
        
        files = []
        for file_data in response_data.get('data', []):
            files.append(File.from_dict(file_data))
        
        return FileListResponse(
            success=response_data.get('success', False),
            data=files,
            pagination=response_data.get('pagination', {})
        )
    
    def get_file(self, file_id: str) -> File:
        """
        Get details of a specific file
        
        Args:
            file_id: ID of the file to retrieve
            
        Returns:
            File object with details
        """
        endpoint = ENDPOINTS['file_detail'].format(id=file_id)
        response_data = self._request('GET', endpoint)
        
        file_data = response_data.get('data', {})
        return File.from_dict(file_data)
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if deletion was successful
        """
        endpoint = ENDPOINTS['file_delete'].format(id=file_id)
        response_data = self._request('DELETE', endpoint)
        
        return response_data.get('success', False)
    
    # FILE TRANSFORMATION METHODS
    
    def get_file_url(
        self,
        file_id: str,
        transform_options: Optional[TransformOptions] = None
    ) -> str:
        """
        Generate URL for file with optional transformations
        
        Args:
            file_id: ID of the file
            transform_options: Image transformation options
            
        Returns:
            URL string for accessing the file
        """
        if transform_options:
            params = transform_options.to_query_params()
            query_string = build_query_params(params)
            endpoint = ENDPOINTS['transform'].format(id=file_id) + query_string
        else:
            endpoint = ENDPOINTS['transform'].format(id=file_id)
        
        return f"{self.api_url}{endpoint}"
    
    def download_file(
        self,
        file_id: str,
        output_path: Union[str, Path],
        transform_options: Optional[TransformOptions] = None
    ) -> str:
        """
        Download file to local path
        
        Args:
            file_id: ID of the file to download
            output_path: Local path to save the file
            transform_options: Optional image transformations
            
        Returns:
            Path where file was saved
        """
        url = self.get_file_url(file_id, transform_options)
        
        response = self.session.get(url, stream=True, timeout=self.timeout)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(output_path)
    
    def get_thumbnail_url(self, file_id: str, size: int = 200) -> str:
        """
        Generate URL for file thumbnail
        
        Args:
            file_id: ID of the file
            size: Thumbnail size in pixels
            
        Returns:
            URL string for thumbnail
        """
        endpoint = ENDPOINTS['thumbnail'].format(id=file_id)
        return f"{self.api_url}{endpoint}?size={size}"
    
    # STATISTICS METHODS
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        response_data = self._request('GET', ENDPOINTS['stats_dashboard'])
        return response_data.get('data', {})
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        response_data = self._request('GET', ENDPOINTS['stats_storage'])
        return response_data.get('data', {})
    
    # BATCH OPERATIONS
    
    def batch_delete_files(self, file_ids: List[str]) -> Dict:
        """
        Delete multiple files in batch
        
        Args:
            file_ids: List of file IDs to delete
            
        Returns:
            Batch operation result
        """
        # Note: This uses the authenticated endpoint, not public
        response_data = self._request(
            'POST',
            '/api/files/bulk-delete',
            json_data={'file_ids': file_ids}
        )
        return response_data
    
    # CONTEXT MANAGER SUPPORT
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the client session"""
        if hasattr(self, 'session'):
            self.session.close()