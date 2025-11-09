"""
Tests for data models
"""

import pytest
from datetime import datetime
from dam_sdk.models import File, Folder, TransformOptions, UploadOptions, SearchOptions

class TestFileModel:
    
    def test_file_creation(self):
        """Test File model creation"""
        file = File(
            id='file-123',
            filename='test.jpg',
            original_name='test.jpg',
            mime_type='image/jpeg',
            size=1024,
            storage_path='user-123/root/test.jpg',
            file_url='http://example.com/file.jpg',
            user_id='user-123'
        )
        
        assert file.id == 'file-123'
        assert file.original_name == 'test.jpg'
        assert file.mime_type == 'image/jpeg'
        assert file.size == 1024
        assert file.is_image is True
        assert file.is_video is False
        assert file.is_document is False
    
    def test_file_from_dict(self):
        """Test File creation from dictionary"""
        data = {
            'id': 'file-123',
            'filename': 'test.jpg',
            'original_name': 'test.jpg',
            'mime_type': 'image/jpeg',
            'size': 1024,
            'storage_path': 'user-123/root/test.jpg',
            'file_url': 'http://example.com/file.jpg',
            'user_id': 'user-123',
            'created_at': '2024-01-01T10:00:00Z',
            'updated_at': '2024-01-01T10:00:00Z'
        }
        
        file = File.from_dict(data)
        
        assert file.id == 'file-123'
        assert file.original_name == 'test.jpg'
        assert isinstance(file.created_at, datetime)
        assert isinstance(file.updated_at, datetime)
    
    def test_file_properties(self):
        """Test File properties"""
        # Image file
        image_file = File(
            id='img-123',
            filename='test.jpg',
            original_name='test.jpg',
            mime_type='image/jpeg',
            size=1024,
            storage_path='path',
            file_url='url',
            user_id='user-123'
        )
        assert image_file.is_image is True
        assert image_file.is_video is False
        
        # Video file
        video_file = File(
            id='vid-123',
            filename='test.mp4',
            original_name='test.mp4',
            mime_type='video/mp4',
            size=1024,
            storage_path='path',
            file_url='url',
            user_id='user-123'
        )
        assert video_file.is_image is False
        assert video_file.is_video is True
        
        # Document file
        doc_file = File(
            id='doc-123',
            filename='test.pdf',
            original_name='test.pdf',
            mime_type='application/pdf',
            size=1024,
            storage_path='path',
            file_url='url',
            user_id='user-123'
        )
        assert doc_file.is_image is False
        assert doc_file.is_document is True

class TestFolderModel:
    
    def test_folder_creation(self):
        """Test Folder model creation"""
        folder = Folder(
            id='folder-123',
            name='My Folder',
            path='/my-folder',
            user_id='user-123'
        )
        
        assert folder.id == 'folder-123'
        assert folder.name == 'My Folder'
        assert folder.path == '/my-folder'
        assert folder.user_id == 'user-123'
    
    def test_folder_from_dict(self):
        """Test Folder creation from dictionary"""
        data = {
            'id': 'folder-123',
            'name': 'My Folder',
            'path': '/my-folder',
            'user_id': 'user-123',
            'parent_folder_id': 'parent-123',
            'description': 'Test folder',
            'color': '#FF0000',
            'created_at': '2024-01-01T10:00:00Z',
            'updated_at': '2024-01-01T10:00:00Z'
        }
        
        folder = Folder.from_dict(data)
        
        assert folder.id == 'folder-123'
        assert folder.name == 'My Folder'
        assert folder.parent_folder_id == 'parent-123'
        assert folder.description == 'Test folder'
        assert folder.color == '#FF0000'
        assert isinstance(folder.created_at, datetime)

class TestTransformOptions:
    
    def test_transform_options_creation(self):
        """Test TransformOptions creation"""
        options = TransformOptions(
            width=800,
            height=600,
            fit='cover',
            format='webp',
            quality=85,
            blur=5,
            grayscale=True,
            rotate=90
        )
        
        assert options.width == 800
        assert options.height == 600
        assert options.fit == 'cover'
        assert options.format == 'webp'
        assert options.quality == 85
        assert options.blur == 5
        assert options.grayscale is True
        assert options.rotate == 90
    
    def test_transform_options_to_query_params(self):
        """Test TransformOptions to query parameters conversion"""
        options = TransformOptions(
            width=800,
            height=600,
            fit='cover',
            format='webp',
            quality=85
        )
        
        params = options.to_query_params()
        
        assert params['w'] == '800'
        assert params['h'] == '600'
        assert params['fit'] == 'cover'
        assert params['format'] == 'webp'
        assert params['quality'] == '85'
    
    def test_transform_options_defaults(self):
        """Test TransformOptions default values"""
        options = TransformOptions()
        
        assert options.width is None
        assert options.height is None
        assert options.fit == 'cover'
        assert options.format is None
        assert options.quality == 80
        assert options.blur is None
        assert options.grayscale is False
        assert options.rotate is None

class TestUploadOptions:
    
    def test_upload_options_creation(self):
        """Test UploadOptions creation"""
        options = UploadOptions(
            folder_id='folder-123',
            metadata={'key': 'value'},
            original_name='custom-name.jpg'
        )
        
        assert options.folder_id == 'folder-123'
        assert options.metadata == {'key': 'value'}
        assert options.original_name == 'custom-name.jpg'
    
    def test_upload_options_defaults(self):
        """Test UploadOptions default values"""
        options = UploadOptions()
        
        assert options.folder_id is None
        assert options.metadata is None
        assert options.original_name is None

class TestSearchOptions:
    
    def test_search_options_creation(self):
        """Test SearchOptions creation"""
        options = SearchOptions(
            folder_id='folder-123',
            mime_type='image/*',
            search='vacation',
            limit=20,
            offset=10,
            sort='size',
            order='asc'
        )
        
        assert options.folder_id == 'folder-123'
        assert options.mime_type == 'image/*'
        assert options.search == 'vacation'
        assert options.limit == 20
        assert options.offset == 10
        assert options.sort == 'size'
        assert options.order == 'asc'
    
    def test_search_options_defaults(self):
        """Test SearchOptions default values"""
        options = SearchOptions()
        
        assert options.folder_id is None
        assert options.mime_type is None
        assert options.search is None
        assert options.limit == 50
        assert options.offset == 0
        assert options.sort == 'created_at'
        assert options.order == 'desc'