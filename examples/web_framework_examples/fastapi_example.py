"""
FastAPI integration example for DAM SDK
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import Optional
import uvicorn

from sdks.python.dam_sdk_py.dam_sdk._init_ import DAMClient, AsyncDAMClient, DAMError

app = FastAPI(title="DAM SDK - FastAPI Demo", version="1.0.0")

# DAM configuration
DAM_CONFIG = {
    'API_URL': os.getenv('DAM_API_URL', 'http://localhost:55055'),
    'KEY_ID': os.getenv('DAM_KEY_ID', 'your-key-id'),
    'KEY_SECRET': os.getenv('DAM_KEY_SECRET', 'your-key-secret'),
}

# HTML template for demo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DAM SDK - FastAPI Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .upload-section, .files-section { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        .upload-form { border: 2px dashed #ccc; padding: 30px; text-align: center; margin: 20px 0; }
        .file-input { margin: 10px 0; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .result { margin: 20px 0; padding: 15px; border-radius: 4px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .file-card { border: 1px solid #eee; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .file-preview { max-width: 100px; max-height: 100px; object-fit: cover; }
    </style>
</head>
<body>
    <h1>🚀 DAM SDK - FastAPI Demo</h1>
    
    <div class="container">
        <div class="upload-section">
            <h2>📤 Upload Files</h2>
            <form id="uploadForm" class="upload-form" enctype="multipart/form-data">
                <div class="file-input">
                    <input type="file" name="file" id="fileInput" required>
                </div>
                <div class="file-input">
                    <input type="text" name="folder_id" placeholder="Folder ID (optional)" id="folderInput">
                </div>
                <button type="submit" class="btn">Upload File</button>
            </form>
            
            <div id="result"></div>
        </div>
        
        <div class="files-section">
            <h2>📁 Your Files</h2>
            <button onclick="loadFiles()" class="btn">Refresh Files</button>
            <div id="filesList"></div>
        </div>
    </div>

    <script>
        // Handle form submission
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('fileInput');
            const folderInput = document.getElementById('folderInput');
            
            formData.append('file', fileInput.files[0]);
            if (folderInput.value) {
                formData.append('folder_id', folderInput.value);
            }
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <div class="success">
                            <strong>✅ Upload Successful!</strong><br>
                            File: ${result.data.original_name}<br>
                            ID: ${result.data.id}<br>
                            <a href="${result.data.file_url}" target="_blank">View Original</a> |
                            <a href="${result.data.thumbnail_url}" target="_blank">View Thumbnail</a>
                        </div>
                    `;
                    fileInput.value = ''; // Reset file input
                    loadFiles(); // Refresh files list
                } else {
                    resultDiv.innerHTML = `<div class="error"><strong>❌ Upload Failed:</strong> ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `<div class="error"><strong>❌ Error:</strong> ${error}</div>`;
            }
        });
        
        // Load files list
        async function loadFiles() {
            try {
                const response = await fetch('/files');
                const result = await response.json();
                const filesList = document.getElementById('filesList');
                
                if (result.success) {
                    if (result.data.length === 0) {
                        filesList.innerHTML = '<p>No files found.</p>';
                        return;
                    }
                    
                    filesList.innerHTML = result.data.map(file => `
                        <div class="file-card">
                            <strong>${file.original_name}</strong><br>
                            <small>Type: ${file.mime_type} | Size: ${file.size} bytes</small><br>
                            ${file.mime_type.startsWith('image/') ? 
                                `<img src="${file.thumbnail_url}" class="file-preview" alt="${file.original_name}">` : 
                                ''}
                            <div>
                                <a href="${file.file_url}" target="_blank">Original</a> |
                                <a href="${file.thumbnail_url}" target="_blank">Thumbnail</a> |
                                <button onclick="deleteFile('${file.id}')">Delete</button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    filesList.innerHTML = `<div class="error">Failed to load files: ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('filesList').innerHTML = `<div class="error">Error loading files: ${error}</div>`;
            }
        }
        
        // Delete file
        async function deleteFile(fileId) {
            if (!confirm('Are you sure you want to delete this file?')) return;
            
            try {
                const response = await fetch(`/files/${fileId}`, { method: 'DELETE' });
                const result = await response.json();
                
                if (result.success) {
                    loadFiles(); // Refresh list
                } else {
                    alert('Delete failed: ' + result.error);
                }
            } catch (error) {
                alert('Error deleting file: ' + error);
            }
        }
        
        // Load files on page load
        loadFiles();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main demo page"""
    return HTML_TEMPLATE

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None)
):
    """Upload file to DAM"""
    try:
        client = DAMClient(**DAM_CONFIG)
        
        # Upload file
        uploaded_file = client.upload_file(
            file.file,
            options={
                'folder_id': folder_id,
                'original_name': file.filename,
                'metadata': {
                    'uploaded_via': 'fastapi_demo',
                    'original_filename': file.filename,
                    'content_type': file.content_type
                }
            }
        )
        
        # Generate transformed URLs
        thumbnail_url = client.get_file_url(uploaded_file.id, {
            'width': 150, 'height': 150, 'fit': 'cover', 'format': 'webp'
        })
        
        return JSONResponse({
            'success': True,
            'data': {
                'id': uploaded_file.id,
                'original_name': uploaded_file.original_name,
                'size': uploaded_file.size,
                'mime_type': uploaded_file.mime_type,
                'file_url': uploaded_file.file_url,
                'thumbnail_url': thumbnail_url
            }
        })
        
    except DAMError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files")
async def list_files(limit: int = 20, offset: int = 0):
    """List uploaded files"""
    try:
        client = DAMClient(**DAM_CONFIG)
        files_response = client.list_files(limit=limit, offset=offset)
        
        files_data = []
        for file in files_response.data:
            thumbnail_url = client.get_file_url(file.id, {
                'width': 100, 'height': 100, 'fit': 'cover', 'format': 'webp'
            })
            
            files_data.append({
                'id': file.id,
                'original_name': file.original_name,
                'size': file.size,
                'mime_type': file.mime_type,
                'file_url': file.file_url,
                'thumbnail_url': thumbnail_url,
                'created_at': file.created_at.isoformat() if file.created_at else None
            })
        
        return JSONResponse({
            'success': True,
            'data': files_data,
            'pagination': files_response.pagination
        })
        
    except DAMError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file"""
    try:
        client = DAMClient(**DAM_CONFIG)
        success = client.delete_file(file_id)
        
        return JSONResponse({
            'success': success,
            'message': 'File deleted successfully' if success else 'Failed to delete file'
        })
        
    except DAMError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get storage statistics"""
    try:
        client = DAMClient(**DAM_CONFIG)
        stats = client.get_dashboard_stats()
        
        return JSONResponse({
            'success': True,
            'data': stats
        })
        
    except DAMError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Async version using AsyncDAMClient
@app.post("/upload-async")
async def upload_file_async(
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None)
):
    """Upload file to DAM (async version)"""
    try:
        async with AsyncDAMClient(**DAM_CONFIG) as client:
            uploaded_file = await client.upload_file(
                file.file,
                options={
                    'folder_id': folder_id,
                    'original_name': file.filename
                }
            )
            
            return JSONResponse({
                'success': True,
                'data': {
                    'id': uploaded_file.id,
                    'original_name': uploaded_file.original_name,
                    'file_url': uploaded_file.file_url
                }
            })
            
    except DAMError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)