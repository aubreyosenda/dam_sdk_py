"""
Django integration example for DAM SDK
"""

# settings.py excerpt
"""
# Add to your Django settings.py
DAM_CONFIG = {
    'API_URL': 'https://your-dam-server.com',
    'KEY_ID': 'your-production-key-id', 
    'KEY_SECRET': 'your-production-key-secret',
    'TIMEOUT': 30,
}
"""

# utils/dam_client.py
import os
from django.conf import settings
from dam_sdk import DAMClient, DAMError

def get_dam_client():
    """Get configured DAM client"""
    config = getattr(settings, 'DAM_CONFIG', {})
    return DAMClient(
        api_url=config.get('API_URL'),
        key_id=config.get('KEY_ID'),
        key_secret=config.get('KEY_SECRET'),
        timeout=config.get('TIMEOUT', 30)
    )

# views.py excerpt
"""
from django.http import JsonResponse
from django.views import View
from .utils.dam_client import get_dam_client

class FileUploadView(View):
    def post(self, request):
        try:
            client = get_dam_client()
            
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'No file provided'}, status=400)
            
            # Upload to DAM
            file_obj = client.upload_file(
                uploaded_file,
                options={
                    'folder_id': request.POST.get('folder_id'),
                    'metadata': {
                        'uploaded_by': request.user.username,
                        'source': 'django_app'
                    }
                }
            )
            
            return JsonResponse({
                'success': True,
                'file': {
                    'id': file_obj.id,
                    'name': file_obj.original_name,
                    'url': file_obj.file_url,
                    'size': file_obj.size
                }
            })
            
        except DAMError as e:
            return JsonResponse({'error': str(e)}, status=400)
"""

# models.py excerpt (if you want to store file references)
"""
from django.db import models

class DAMFile(models.Model):
    dam_file_id = models.CharField(max_length=255, unique=True)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    file_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_thumbnail_url(self, size=150):
        from .utils.dam_client import get_dam_client
        client = get_dam_client()
        return client.get_file_url(self.dam_file_id, {
            'width': size, 
            'height': size, 
            'fit': 'cover',
            'format': 'webp'
        })
"""