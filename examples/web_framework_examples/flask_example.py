"""
Flask integration example for DAM SDK
"""

from flask import Flask, request, jsonify, render_template_string
import os
from sdks.python.dam_sdk_py.dam_sdk._init_ import DAMClient, DAMError

app = Flask(__name__)

# DAM configuration
DAM_CONFIG = {
    'API_URL': os.getenv('DAM_API_URL', 'http://localhost:55055'),
    'KEY_ID': os.getenv('DAM_KEY_ID', 'your-key-id'),
    'KEY_SECRET': os.getenv('DAM_KEY_SECRET', 'your-key-secret'),
}

def get_dam_client():
    """Get configured DAM client"""
    return DAMClient(**DAM_CONFIG)

# HTML template for demo
UPLOAD_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>DAM SDK - Flask Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .upload-form { border: 2px dashed #ccc; padding: 30px; text-align: center; margin: 20px 0; }
        .file-input { margin: 10px 0; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .result { margin: 20px 0; padding: 15px; border-radius: 4px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .file-info { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🚀 DAM SDK - Flask Demo</h1>
    
    <form method="POST" action="/upload" enctype="multipart/form-data" class="upload-form">
        <h3>Upload File to DAM</h3>
        <div class="file-input">
            <input type="file" name="file" required>
        </div>
        <div class="file-input">
            <input type="text" name="folder_id" placeholder="Folder ID (optional)">
        </div>
        <button type="submit" class="btn">Upload File</button>
    </form>

    {% if result %}
        <div class="result {% if result.success %}success{% else %}error{% endif %}">
            {{ result.message }}
        </div>
        
        {% if result.file %}
        <div class="file-info">
            <h4>📁 File Information:</h4>
            <p><strong>ID:</strong> {{ result.file.id }}</p>
            <p><strong>Name:</strong> {{ result.file.original_name }}</p>
            <p><strong>Size:</strong> {{ result.file.size }} bytes</p>
            <p><strong>Type:</strong> {{ result.file.mime_type }}</p>
            <p><strong>URL:</strong> <a href="{{ result.file.file_url }}" target="_blank">{{ result.file.file_url }}</a></p>
            
            <h4>🖼️ Transformed URLs:</h4>
            <p><strong>Thumbnail (150x150):</strong> 
                <a href="{{ result.thumbnail_url }}" target="_blank">View</a>
            </p>
            <p><strong>Web Optimized (800x600):</strong> 
                <a href="{{ result.web_url }}" target="_blank">View</a>
            </p>
        </div>
        {% endif %}
    {% endif %}

    <hr>
    <h3>📊 Storage Statistics</h3>
    <a href="/stats" class="btn">View Storage Stats</a>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template_string(UPLOAD_FORM)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        client = get_dam_client()
        
        if 'file' not in request.files:
            return render_template_string(UPLOAD_FORM, result={
                'success': False,
                'message': 'No file selected'
            })
        
        file = request.files['file']
        folder_id = request.form.get('folder_id')
        
        if file.filename == '':
            return render_template_string(UPLOAD_FORM, result={
                'success': False,
                'message': 'No file selected'
            })
        
        # Upload to DAM
        uploaded_file = client.upload_file(
            file.stream,
            options={
                'folder_id': folder_id,
                'original_name': file.filename,
                'metadata': {
                    'uploaded_via': 'flask_demo',
                    'original_filename': file.filename
                }
            }
        )
        
        # Generate transformed URLs
        thumbnail_url = client.get_file_url(uploaded_file.id, {
            'width': 150, 'height': 150, 'fit': 'cover', 'format': 'webp'
        })
        
        web_url = client.get_file_url(uploaded_file.id, {
            'width': 800, 'height': 600, 'fit': 'contain', 'format': 'webp', 'quality': 80
        })
        
        return render_template_string(UPLOAD_FORM, result={
            'success': True,
            'message': f'File "{uploaded_file.original_name}" uploaded successfully!',
            'file': {
                'id': uploaded_file.id,
                'original_name': uploaded_file.original_name,
                'size': uploaded_file.size,
                'mime_type': uploaded_file.mime_type,
                'file_url': uploaded_file.file_url
            },
            'thumbnail_url': thumbnail_url,
            'web_url': web_url
        })
        
    except DAMError as e:
        return render_template_string(UPLOAD_FORM, result={
            'success': False,
            'message': f'Upload failed: {str(e)}'
        })
    except Exception as e:
        return render_template_string(UPLOAD_FORM, result={
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        })

@app.route('/stats')
def get_stats():
    """Get storage statistics"""
    try:
        client = get_dam_client()
        stats = client.get_dashboard_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except DAMError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/files')
def list_files():
    """List uploaded files"""
    try:
        client = get_dam_client()
        files_response = client.list_files(limit=20)
        
        files_data = []
        for file in files_response.data:
            files_data.append({
                'id': file.id,
                'name': file.original_name,
                'size': file.size,
                'type': file.mime_type,
                'url': file.file_url,
                'created_at': file.created_at.isoformat() if file.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': files_data,
            'pagination': files_response.pagination
        })
        
    except DAMError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)