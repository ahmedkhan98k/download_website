/*
============================================
    Social Downloader Website
    Developed by: Ahmed Khan (أحمد خان)
    Instagram: @_98sf
    Telegram: @AHMED_KHANA
    All Rights Reserved © 2024
============================================
*/

console.log('%c🚀 Social Downloader', 'color: #667eea; font-size: 20px; font-weight: bold');
console.log('%c👨‍💻 Developed by: Ahmed Khan (@_98sf)', 'color: #764ba2; font-size: 16px');
console.log('%c📱 Telegram: @AHMED_KHANA', 'color: #0088cc; font-size: 14px');
console.log('%c📱 Instagram: @_98sf', 'color: #E4405F; font-size: 14px');

// انتظار تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('urlInput');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorMessage = document.getElementById('errorMessage');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultContainer = document.getElementById('resultContainer');
    const thumbnailContainer = document.getElementById('thumbnailContainer');
    const videoTitle = document.getElementById('videoTitle');
    const videoInfo = document.getElementById('videoInfo');
    const downloadFileBtn = document.getElementById('downloadFileBtn');
    const newDownloadBtn = document.getElementById('newDownloadBtn');
    
    // التحقق من الرابط عند اللصق
    urlInput.addEventListener('paste', function(e) {
        setTimeout(validateUrl, 100);
    });
    
    urlInput.addEventListener('input', function() {
        hideError();
    });
    
    // زر التحميل
    downloadBtn.addEventListener('click', function() {
        const url = urlInput.value.trim();
        if (url) {
            startDownload(url);
        } else {
            showError('الرجاء إدخال رابط');
        }
    });
    
    // Enter في حقل الإدخال
    urlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            downloadBtn.click();
        }
    });
    
    // تحميل ملف جديد
    newDownloadBtn?.addEventListener('click', function() {
        resetForm();
    });
    
    // دوال مساعدة
    function validateUrl() {
        const url = urlInput.value.trim();
        if (!url) return;
        
        fetch('/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                urlInput.classList.add('is-valid');
                urlInput.classList.remove('is-invalid');
            } else {
                urlInput.classList.add('is-invalid');
                urlInput.classList.remove('is-valid');
                showError('الرابط غير مدعوم');
            }
        })
        .catch(error => {
            console.error('Validation error:', error);
        });
    }
    
    function startDownload(url) {
        // إخفاء النتائج السابقة
        hideError();
        resultContainer.classList.add('d-none');
        loadingIndicator.classList.remove('d-none');
        downloadBtn.disabled = true;
        
        fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('d-none');
            downloadBtn.disabled = false;
            
            if (data.success) {
                showResult(data.data);
            } else {
                showError(data.error || 'حدث خطأ في التحميل');
            }
        })
        .catch(error => {
            console.error('Download error:', error);
            loadingIndicator.classList.add('d-none');
            downloadBtn.disabled = false;
            showError('حدث خطأ في الاتصال بالخادم');
        });
    }
    
    function showResult(data) {
        // عرض الصورة المصغرة
        if (data.thumbnail) {
            thumbnailContainer.innerHTML = `
                <img src="${data.thumbnail}" class="img-fluid rounded" alt="صورة مصغرة">
            `;
        } else {
            thumbnailContainer.innerHTML = `
                <div class="bg-light p-4 text-center rounded">
                    <i class="fas fa-file-video fa-4x text-primary"></i>
                </div>
            `;
        }
        
        // عنوان الفيديو
        videoTitle.textContent = data.title || 'فيديو بدون عنوان';
        
        // معلومات إضافية
        let info = [];
        if (data.platform) {
            info.push(`المنصة: ${getPlatformName(data.platform)}`);
        }
        if (data.duration) {
            const minutes = Math.floor(data.duration / 60);
            const seconds = data.duration % 60;
            info.push(`المدة: ${minutes}:${seconds.toString().padStart(2, '0')}`);
        }
        if (data.type) {
            info.push(`النوع: ${data.type === 'video' ? 'فيديو' : 'صورة'}`);
        }
        videoInfo.textContent = info.join(' | ');
        
        // زر التحميل
        downloadFileBtn.onclick = function() {
            downloadFile(data.url, getFileName(data));
        };
        
        // حفظ البيانات للصفحة الجديدة
        localStorage.setItem('downloadResult', JSON.stringify({
            success: true,
            data: data
        }));
        
        // عرض النتيجة
        resultContainer.classList.remove('d-none');
        
        // تمرير سلس للنتيجة
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    function downloadFile(url, filename) {
        fetch('/api/download-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url, filename: filename })
        })
        .then(response => response.blob())
        .then(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            URL.revokeObjectURL(link.href);
        })
        .catch(error => {
            console.error('File download error:', error);
            window.open(url, '_blank');
        });
    }
    
    function getFileName(data) {
        const platform = data.platform || 'download';
        const type = data.type === 'video' ? 'mp4' : 'jpg';
        const date = new Date().toISOString().slice(0,10);
        return `${platform}_${date}.${type}`;
    }
    
    function getPlatformName(platform) {
        const names = {
            'tiktok': 'تيك توك',
            'facebook': 'فيسبوك',
            'instagram': 'انستجرام',
            'youtube': 'يوتيوب',
            'pinterest': 'بنترست',
            'snapchat': 'سناب شات'
        };
        return names[platform] || platform;
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
        urlInput.classList.add('is-invalid');
    }
    
    function hideError() {
        errorMessage.classList.add('d-none');
        urlInput.classList.remove('is-invalid');
    }
    
    function resetForm() {
        urlInput.value = '';
        urlInput.classList.remove('is-valid', 'is-invalid');
        resultContainer.classList.add('d-none');
        hideError();
        urlInput.focus();
    }
});
