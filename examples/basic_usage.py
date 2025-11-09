#!/usr/bin/env python3
"""
Basic usage examples for DAM Python SDK
"""

import os
from pathlib import Path
from dam_sdk import DAMClient, TransformOptions, UploadOptions

def main():
    # Initialize client
    client = DAMClient(
        api_url=os.getenv('DAM_API_URL', 'http://localhost:55055'),
        key_id=os.getenv('DAM_KEY_ID', 'your-key-id'),
        key_secret=os.getenv('DAM_KEY_SECRET', 'your-key-secret')
    )
    
    print("🚀 DAM Python SDK Demo")
    print("=" * 50)
    
    # 1. Upload a file
    print("\n1. Uploading file...")
    try:
        # Create a test file if it doesn't exist
        test_file = Path("test_image.jpg")
        if not test_file.exists():
            # Create a simple 1x1 pixel red image
            from PIL import Image
            img = Image.new('RGB', (1, 1), color='red')
            img.save(test_file)
        
        file = client.upload_file(test_file)
        print(f"✅ Uploaded: {file.original_name}")
        print(f"   File ID: {file.id}")
        print(f"   Size: {file.size} bytes")
        print(f"   URL: {file.file_url}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # 2. List files
    print("\n2. Listing files...")
    try:
        files_response = client.list_files(limit=5)
        print(f"✅ Found {len(files_response.data)} files")
        
        for f in files_response.data:
            print(f"   - {f.original_name} ({f.mime_type})")
            
    except Exception as e:
        print(f"❌ List files failed: {e}")
    
    # 3. Get file details
    print("\n3. Getting file details...")
    try:
        file_details = client.get_file(file.id)
        print(f"✅ File details:")
        print(f"   Name: {file_details.original_name}")
        print(f"   Type: {file_details.mime_type}")
        print(f"   Is Image: {file_details.is_image}")
        print(f"   Created: {file_details.created_at}")
        
    except Exception as e:
        print(f"❌ Get file failed: {e}")
    
    # 4. Generate transformed URLs
    print("\n4. Generating transformed URLs...")
    try:
        # Thumbnail
        thumb_url = client.get_file_url(file.id, TransformOptions(
            width=150, height=150, fit='cover', format='webp'
        ))
        print(f"✅ Thumbnail URL: {thumb_url}")
        
        # Web-optimized
        web_url = client.get_file_url(file.id, TransformOptions(
            width=1200, quality=80, format='webp'
        ))
        print(f"✅ Web-optimized URL: {web_url}")
        
    except Exception as e:
        print(f"❌ Transform URL failed: {e}")
    
    # 5. Get statistics
    print("\n5. Getting statistics...")
    try:
        stats = client.get_dashboard_stats()
        if stats and 'overview' in stats:
            overview = stats['overview']
            print(f"✅ Storage Stats:")
            print(f"   Files: {overview.get('fileCount', 0)}")
            print(f"   Folders: {overview.get('folderCount', 0)}")
            print(f"   Total Size: {overview.get('totalSizeFormatted', '0 Bytes')}")
            
    except Exception as e:
        print(f"❌ Stats failed: {e}")
    
    # 6. Cleanup (delete test file)
    print("\n6. Cleaning up...")
    try:
        # Delete the uploaded file
        success = client.delete_file(file.id)
        if success:
            print(f"✅ Deleted file: {file.id}")
        else:
            print(f"❌ Failed to delete file")
            
        # Delete local test file
        if test_file.exists():
            test_file.unlink()
            print("✅ Deleted local test file")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    main()