from flask import Flask, request, jsonify
import subprocess
import requests
import os
import tempfile

app = Flask(__name__)

@app.route('/merge-video', methods=['POST'])
def merge_video():
    try:
        data = request.json
        voice_url = data.get('voice_url')
        video_url = data.get('video_url')
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        # Download files
        voice_path = os.path.join(temp_dir, 'voice.mp3')
        video_path = os.path.join(temp_dir, 'video.mp4')
        output_path = os.path.join(temp_dir, 'final.mp4')
        
        # Download voice
        voice_response = requests.get(voice_url)
        with open(voice_path, 'wb') as f:
            f.write(voice_response.content)
        
        # Download video
        video_response = requests.get(video_url)
        with open(video_path, 'wb') as f:
            f.write(video_response.content)
        
        # Merge with FFmpeg
        subprocess.run([
            'ffmpeg', '-i', video_path, '-i', voice_path,
            '-c:v', 'copy', '-c:a', 'aac', '-shortest',
            output_path
        ], check=True)
        
        # Read merged file
        with open(output_path, 'rb') as f:
            merged_video = f.read()
        
        return jsonify({
            'success': True,
            'message': 'Video merged successfully',
            'size': len(merged_video)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
