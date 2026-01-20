"""
Srijan Engine - Minimal Web Server
Quick startup version
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def dashboard():
    """Main workflow dashboard"""
    return render_template('workflow_dashboard.html')

@app.route('/api/status')
def status():
    return jsonify({'status': 'online', 'timestamp': datetime.now().isoformat()})

@app.route('/api/output-files', methods=['GET'])
def list_files():
    """List all output files"""
    files = {'videos': [], 'audio': [], 'subtitles': [], 'total_size_mb': 0}
    
    if os.path.exists(OUTPUT_FOLDER):
        for filename in os.listdir(OUTPUT_FOLDER):
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            if os.path.isfile(filepath):
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                info = {'name': filename, 'size_mb': round(size_mb, 2), 'path': filepath}
                
                if filename.endswith('.mp4'):
                    files['videos'].append(info)
                elif filename.endswith('.wav'):
                    files['audio'].append(info)
                elif filename.endswith('.srt'):
                    files['subtitles'].append(info)
                
                files['total_size_mb'] += size_mb
    
    return jsonify({'success': True, 'files': files, 'total_size_mb': round(files['total_size_mb'], 2)})

@app.route('/download/<filename>')
def download(filename):
    """Download file"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SRIJAN ENGINE - MINIMAL SERVER")
    print("="*60)
    print("📍 Open: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
