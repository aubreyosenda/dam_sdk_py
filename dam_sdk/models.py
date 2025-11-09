"""Data models for the DAM SDK"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class File:
    """Represents a file in the DAM system"""
    id: str
    filename: str
    original_name: str
    mime_type: str
    size: int
    storage_path: str
    file_url: str
    user_id: str
    folder_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    is_public: bool = True
    download_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith('image/')
    
    @property
    def is_video(self) -> bool:
        return self.mime_type.startswith('video/')
    
    @property
    def is_document(self) -> bool:
        document_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        return self.mime_type in document_types
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'File':
        """Create File instance from API response data"""
        # Handle datetime conversion
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        
        if created_at and isinstance(created_at, str):
            data['created_at'] = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if updated_at and isinstance(updated_at, str):
            data['updated_at'] = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
        return cls(**data)

@dataclass
class Folder:
    """Represents a folder in the DAM system"""
    id: str
    name: str
    path: str
    user_id: str
    parent_folder_id: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Folder':
        """Create Folder instance from API response data"""
        # Handle datetime conversion
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        
        if created_at and isinstance(created_at, str):
            data['created_at'] = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if updated_at and isinstance(updated_at, str):
            data['updated_at'] = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
        return cls(**data)

@dataclass
class UploadResponse:
    """Response from file upload operations"""
    success: bool
    message: str
    data: Union[File, List[File]]
    failed: Optional[List[Dict[str, Any]]] = None
    counts: Optional[Dict[str, int]] = None

@dataclass
class FileListResponse:
    """Response from file listing operations"""
    success: bool
    data: List[File]
    pagination: Dict[str, Any]

@dataclass
class TransformOptions:
    """Options for image transformations"""
    width: Optional[int] = None
    height: Optional[int] = None
    fit: str = 'cover'
    format: Optional[str] = None
    quality: int = 80
    blur: Optional[int] = None
    grayscale: bool = False
    rotate: Optional[int] = None
    
    def to_query_params(self) -> Dict[str, str]:
        """Convert to query parameters for API request"""
        params = {}
        if self.width:
            params['w'] = str(self.width)
        if self.height:
            params['h'] = str(self.height)
        if self.fit:
            params['fit'] = self.fit
        if self.format:
            params['format'] = self.format
        if self.quality:
            params['quality'] = str(self.quality)
        if self.blur:
            params['blur'] = str(self.blur)
        if self.grayscale:
            params['grayscale'] = 'true'
        if self.rotate:
            params['rotate'] = str(self.rotate)
        return params

@dataclass
class UploadOptions:
    """Options for file uploads"""
    folder_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    original_name: Optional[str] = None

@dataclass
class SearchOptions:
    """Options for file search"""
    folder_id: Optional[str] = None
    mime_type: Optional[str] = None
    search: Optional[str] = None
    limit: int = 50
    offset: int = 0
    sort: str = 'created_at'
    order: str = 'desc'