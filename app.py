from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_cors import CORS
import asyncio
import os
import tempfile
import requests
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import logging

from downloaders import download_media, download_bytes
from config import Config

# إعداد التطبيق
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# التأكد من وجود مجلد الرفع
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

"""
============================================
    Social Downloader Web Application
    Developed by: Ahmed Khan (أحمد خان)
    Instagram: @_98sf
    Telegram: @AHMED_KHANA
    All Rights Reserved © 2024
============================================
"""

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/about')
def about():
    """صفحة عن المطور"""
    return render_template('about.html')

@app.route('/api/download', methods=['POST'])
def api_download():
    """API للتحميل"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'الرجاء إدخال رابط'})
        
        if not url.startswith(('http://', 'https://')):
            return jsonify({'success': False, 'error': 'الرابط غير صالح'})
        
        # التحميل
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(download_media(url))
        loop.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'message': 'تم التحميل بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'حدث خطأ في التحميل')
            })
            
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download-file', methods=['POST'])
def download_file():
    """تحميل الملف مباشرة"""
    try:
        data = request.get_json()
        file_url = data.get('url', '')
        filename = data.get('filename', 'download.mp4')
        
        response = requests.get(file_url, stream=True, timeout=30)
        response.raise_for_status()
        
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, secure_filename(filename))
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Download file error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validate', methods=['POST'])
def validate_url():
    """التحقق من صحة الرابط"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'valid': False, 'platform': None})
        
        url_lower = url.lower()
        platform = None
        
        if "tiktok.com" in url_lower:
            platform = "tiktok"
        elif "facebook.com" in url_lower or "fb.com" in url_lower or "fb.watch" in url_lower:
            platform = "facebook"
        elif "instagram.com" in url_lower or "instagr.am" in url_lower:
            platform = "instagram"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            platform = "youtube"
        elif "pin.it" in url_lower or "pinterest.com" in url_lower:
            platform = "pinterest"
        elif "snapchat.com" in url_lower:
            platform = "snapchat"
        
        return jsonify({
            'valid': platform is not None,
            'platform': platform
        })
        
    except Exception as e:
        logger.error(f"Validate error: {e}")
        return jsonify({'valid': False, 'platform': None})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', error='الصفحة غير موجودة'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', error='حدث خطأ داخلي'), 500

if __name__ == '__main__':
    print("="*50)
    print("🚀 Social Downloader - Developed by Ahmed Khan")
    print("📱 Instagram: @_98sf")
    print("📱 Telegram: @AHMED_KHANA")
    print("="*50)
    app.run(debug=True, host='0.0.0.0', port=5000)
