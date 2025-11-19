from flask import Flask, request, jsonify
import subprocess
import requests
import os
import tempfile
import re

app = Flask(__name__)

def get_google_drive_download_url(url):
    """Convert Google Drive URL to direct download URL"""
    # Extract file ID from various Google Drive URL formats
    file_id = None
    
    if 'drive.google.com/uc?export=download&id=' in url:
        file_id = url.split('id=')[1].split('&')[0]
    elif 'drive.google.com/file/d/' in url:
        file_id = url.split('/d/')[1].split('/')[0]
    elif '/open?id=' in url:
        file_id = url.split('id=')[1].split('&')[0]
    
    if file_id:
        return f'https://drive.google.com/uc?export=download&id={file_id}&confirm=t'
    return url

@app.route('/merge-video', methods=['POST'])
def merge_video():
    try:
        data = request.json
        voice_url = get_google_drive_download_url(data.get('voice_url'))
        video_url = get_google_drive_download_url(data.get('video_url'))
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        # Download files
        voice_path = os.path.join(temp_dir, 'voice.mp3')
        video_path = os.path.join(temp_dir, 'video.mp4')
        output_path = os.path.join(temp_dir, 'final.mp4')
        
        # Download voice with headers
        session = requests.Session()
        voice_response = session.get(voice_url, allow_redirects=True)
        with open(voice_path, 'wb') as f:
            f.write(voice_response.content)
        
        # Download video with headers
        video_response = session.get(video_url, allow_redirects=True)
        with open(video_path, 'wb') as f:
            f.write(video_response.content)
        
        # Merge with FFmpeg
        result = subprocess.run([
            'ffmpeg', '-i', video_path, '-i', voice_path,
            '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-y',
            output_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({
                'success': False, 
                'error': 'FFmpeg error',
                'details': result.stderr
            }), 500
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        return jsonify({
            'success': True,
            'message': 'Video merged successfully',
            'size': file_size
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
