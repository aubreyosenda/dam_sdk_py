#!/usr/bin/env python3
"""
Async usage examples for DAM Python SDK
"""

import asyncio
import os
from pathlib import Path
from dam_sdk import AsyncDAMClient

async def async_demo():
    print("⚡ Async DAM SDK Demo")
    print("=" * 50)
    
    async with AsyncDAMClient(
        api_url=os.getenv('DAM_API_URL', 'http://localhost:55055'),
        key_id=os.getenv('DAM_KEY_ID', 'your-key-id'),
        key_secret=os.getenv('DAM_KEY_SECRET', 'your-key-secret')
    ) as client:
        
        # 1. Upload multiple files concurrently
        print("\n1. Uploading files concurrently...")
        
        # Create test files
        test_files = []
        for i in range(3):
            file_path = Path(f"test_async_{i}.jpg")
            if not file_path.exists():
                from PIL import Image
                img = Image.new('RGB', (10, 10), color=(i * 80, i * 80, i * 80))
                img.save(file_path)
            test_files.append(file_path)
        
        # Upload files one by one (in real app, you might use asyncio.gather)
        uploaded_files = []
        for file_path in test_files:
            try:
                file = await client.upload_file(file_path)
                uploaded_files.append(file)
                print(f"✅ Uploaded: {file.original_name}")
            except Exception as e:
                print(f"❌ Failed to upload {file_path}: {e}")
        
        # 2. List files async
        print("\n2. Listing files asynchronously...")
        try:
            files_response = await client.list_files(limit=10)
            print(f"✅ Found {len(files_response.data)} files")
        except Exception as e:
            print(f"❌ List files failed: {e}")
        
        # 3. Get file details async
        print("\n3. Getting file details asynchronously...")
        if uploaded_files:
            try:
                file_details = await client.get_file(uploaded_files[0].id)
                print(f"✅ File: {file_details.original_name}")
                print(f"   Is Image: {file_details.is_image}")
            except Exception as e:
                print(f"❌ Get file failed: {e}")
        
        # 4. Cleanup
        print("\n4. Cleaning up...")
        for file in uploaded_files:
            try:
                success = await client.delete_file(file.id)
                if success:
                    print(f"✅ Deleted: {file.original_name}")
            except Exception as e:
                print(f"❌ Failed to delete {file.original_name}: {e}")
        
        # Delete local test files
        for file_path in test_files:
            if file_path.exists():
                file_path.unlink()
        
        print("✅ Deleted local test files")
    
    print("\n🎉 Async demo completed!")

if __name__ == "__main__":
    asyncio.run(async_demo())