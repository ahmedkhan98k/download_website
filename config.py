import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ahmed-khan-secret-key-2024'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'jpg', 'jpeg', 'png', 'gif'}
    
    # API URLs
    TIKTOK_API_URL = "https://www.tikwm.com/api/"
    PINTEREST_API_URL = "https://everyweb.net/wp-json/aio-dl/video-data/"
    FB_API_URL = "https://fbdownloader.to/api/ajaxSearch"
    
    # Tokens
    PINTEREST_TOKEN = "0d8a45597e998fd21242b74089fac11b70dd1499a2ba25ad3b6100238811eafd"
    YOUTUBE_RAPIDAPI_KEY = "ccbf5c7fb7mshe66aa640fe34327p188362jsn8c8ef10771d3"
