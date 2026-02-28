import logging
import requests
from user_agent import generate_user_agent
import os
from bs4 import BeautifulSoup
import yt_dlp
import re
import instaloader
import json
import urllib.parse
import time
from typing import Optional, Dict, Any, List
from io import BytesIO
import tempfile

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
============================================
    Social Downloader - Download Module
    Developed by: Ahmed Khan (أحمد خان)
    Instagram: @_98sf
    Telegram: @AHMED_KHANA
    All Rights Reserved © 2024
============================================
"""

# الهيدرات
TIKTOK_HEADERS = {
    'authority': 'www.tikwm.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'ar,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

PINTEREST_HEADERS = {
    'authority': 'everyweb.net',
    'accept': '*/*',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

FB_HEADERS = {
    'authority': 'fbdownloader.to',
    'accept': '*/*',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

SNAPCHAT_HEADERS = {
    'authority': 'snapinsta.app',
    'accept': '*/*',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# دوال مساعدة
def safe_filename_from_url(url: str, default: str) -> str:
    try:
        tail = urllib.parse.urlparse(url).path.split('/')[-1]
        if not tail:
            return default
        if '.' not in tail:
            return f"{tail}.bin"
        return tail
    except:
        return default

def download_bytes(url: str, timeout: int = 20) -> bytes:
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    return r.content

def extract_youtube_id(url: str) -> Optional[str]:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu.be\/([0-9A-Za-z_-]{11})',
        r'embed\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# دوال التحميل
async def download_tiktok(url: str) -> Dict[str, Any]:
    """تحميل من تيك توك - Developed by Ahmed Khan"""
    result = {'success': False, 'data': None, 'error': None}
    
    try:
        headers = TIKTOK_HEADERS.copy()
        data = {'url': url, 'count': '12', 'cursor': '0', 'web': '1', 'hd': '1'}
        
        response = requests.post('https://www.tikwm.com/api/', headers=headers, data=data, timeout=20)
        response.raise_for_status()
        
        result_data = response.json()
        if result_data.get('code') == 0:
            data = result_data.get('data', {})
            
            video_url = None
            if data.get('hdplay'):
                video_url = 'https://www.tikwm.com' + data['hdplay']
            elif data.get('play'):
                video_url = 'https://www.tikwm.com' + data['play']
            
            if video_url:
                result['success'] = True
                result['data'] = {
                    'url': video_url,
                    'type': 'video',
                    'title': data.get('title', 'تيك توك'),
                    'duration': data.get('duration'),
                    'thumbnail': data.get('cover'),
                    'platform': 'tiktok'
                }
                return result
    except Exception as e:
        logger.error(f"TikTok download error: {e}")
        result['error'] = str(e)
    
    return result

async def download_facebook(url: str) -> Dict[str, Any]:
    """تحميل من فيسبوك - Developed by Ahmed Khan"""
    result = {'success': False, 'data': None, 'error': None}
    
    try:
        data = {
            'k_exp': '1753825936',
            'k_token': '2ba09b483e6bd112275af34aa9fa4c2a9d53df34a934389b8086bcbffce0a515',
            'p': 'home',
            'q': url,
            'lang': 'ar',
            'v': 'v2',
            'w': '',
        }
        
        response = requests.post('https://fbdownloader.to/api/ajaxSearch', headers=FB_HEADERS, data=data, timeout=20)
        response.raise_for_status()
        json_data = response.json()
        
        if json_data.get('status') == 'ok':
            soup = BeautifulSoup(json_data['data'], 'html.parser')
            video_url = None
            
            for quality in ['720p (HD)', '360p (SD)']:
                link = soup.find('a', {'title': f'Download {quality}'})
                if link and 'href' in link.attrs:
                    video_url = link['href']
                    break
            
            if video_url:
                result['success'] = True
                result['data'] = {
                    'url': video_url,
                    'type': 'video',
                    'title': 'فيسبوك فيديو',
                    'platform': 'facebook'
                }
    except Exception as e:
        logger.error(f"Facebook download error: {e}")
        result['error'] = str(e)
    
    return result

async def download_instagram(url: str) -> Dict[str, Any]:
    """تحميل من انستجرام - Developed by Ahmed Khan"""
    result = {'success': False, 'data': None, 'error': None}
    
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'socket_timeout': 15,
            'no_check_certificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            if info.get('duration', 0) > 0:
                result['success'] = True
                result['data'] = {
                    'url': info['url'],
                    'type': 'video',
                    'title': info.get('title', 'انستجرام'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'platform': 'instagram'
                }
            else:
                result['success'] = True
                result['data'] = {
                    'url': info['url'],
                    'type': 'image',
                    'title': info.get('title', 'انستجرام'),
                    'thumbnail': info.get('thumbnail'),
                    'platform': 'instagram'
                }
    except Exception as e:
        logger.error(f"Instagram download error: {e}")
        result['error'] = str(e)
    
    return result

async def download_youtube(url: str) -> Dict[str, Any]:
    """تحميل من يوتيوب - Developed by Ahmed Khan"""
    result = {'success': False, 'data': None, 'error': None}
    
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'socket_timeout': 15,
            'no_check_certificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            result['success'] = True
            result['data'] = {
                'url': info['url'],
                'type': 'video',
                'title': info.get('title', 'يوتيوب'),
                'duration': info.get('duration'),
                'thumbnail': info.get('thumbnail'),
                'platform': 'youtube'
            }
    except Exception as e:
        logger.error(f"YouTube download error: {e}")
        result['error'] = str(e)
    
    return result

async def download_pinterest(url: str) -> Dict[str, Any]:
    """تحميل من بنترست - Developed by Ahmed Khan"""
    result = {'success': False, 'data': None, 'error': None}
    
    try:
        # محاولة تحميل الصورة
        headers = {
            'authority': 'api.pinterestdl.io',
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get('https://api.pinterestdl.io/api/image', params={'url': url}, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            image_url = data.get('imageUrl')
            if image_url:
                result['success'] = True
                result['data'] = {
                    'url': image_url,
                    'type': 'image',
                    'title': 'بنتريست صورة',
                    'platform': 'pinterest'
                }
                return result
        
        # محاولة تحميل الفيديو
        data_form = {'url': url, 'token': '0d8a45597e998fd21242b74089fac11b70dd1499a2ba25ad3b6100238811eafd'}
        video_response = requests.post(
            'https://everyweb.net/wp-json/aio-dl/video-data/',
            data=data_form,
            timeout=20
        )
        
        if video_response.status_code == 200:
            jd = video_response.json()
            medias = jd.get('medias') or []
            if medias:
                video_url = medias[0].get('url')
                if video_url:
                    result['success'] = True
                    result['data'] = {
                        'url': video_url,
                        'type': 'video',
                        'title': 'بنتريست فيديو',
                        'platform': 'pinterest'
                    }
    except Exception as e:
        logger.error(f"Pinterest download error: {e}")
        result['error'] = str(e)
    
    return result

async def download_snapchat(url: str) -> Dict[str, Any]:
    """تحميل من سناب شات - Developed by Ahmed Khan"""
    result = {'success': False, 'data': None, 'error': None}
    
    try:
        data = {'url': url, 'action': 'post'}
        response = requests.post('https://snapinsta.app/action.php', headers=SNAPCHAT_HEADERS, data=data, timeout=20)
        response.raise_for_status()
        
        json_data = response.json()
        if json_data.get('status') == 'success' and 'url' in json_data:
            result['success'] = True
            result['data'] = {
                'url': json_data['url'],
                'type': 'video',
                'title': 'سناب شات',
                'platform': 'snapchat'
            }
    except Exception as e:
        logger.error(f"Snapchat download error: {e}")
        result['error'] = str(e)
    
    return result

# الدالة الرئيسية
async def download_media(url: str) -> Dict[str, Any]:
    """تحديد المنصة والتحميل - Developed by Ahmed Khan"""
    url_lower = url.lower()
    
    if "tiktok.com" in url_lower:
        return await download_tiktok(url)
    elif "facebook.com" in url_lower or "fb.com" in url_lower or "fb.watch" in url_lower:
        return await download_facebook(url)
    elif "instagram.com" in url_lower or "instagr.am" in url_lower:
        return await download_instagram(url)
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return await download_youtube(url)
    elif "pin.it" in url_lower or "pinterest.com" in url_lower:
        return await download_pinterest(url)
    elif "snapchat.com" in url_lower:
        return await download_snapchat(url)
    else:
        return {'success': False, 'error': 'الرابط غير مدعوم'}
