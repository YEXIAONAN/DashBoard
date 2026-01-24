from django.utils.deprecation import MiddlewareMixin
from datetime import datetime
import time
import hashlib
import random

class CacheControlMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # 跳过静态文件路径，让Django使用默认的静态文件处理
        if request.path.startswith('/static/'):
            return response
            
        # 生成唯一的ETag
        etag_content = f"{time.time()}_{random.randint(1000, 9999)}_{request.path}"
        etag = hashlib.md5(etag_content.encode()).hexdigest()
        
        # 为所有响应添加极其严格的缓存控制头
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, post-check=0, pre-check=0, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Surrogate-Control'] = 'no-store, no-cache, must-revalidate'
        response['Vary'] = '*, User-Agent, Accept-Encoding, Accept-Language'
        response['ETag'] = f'"{etag}"'
        response['Age'] = '0'
        
        # 添加额外的防止缓存头
        if 'Last-Modified' not in response:
            response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 添加时间戳URL参数强制刷新
        if '?' not in request.get_full_path():
            response['Location'] = request.get_full_path() + f'?_t={int(time.time())}'
        
        # 确保HTML页面不被缓存
        if response.get('Content-Type', '').startswith('text/html'):
            response['Cache-Control'] += ', no-transform, proxy-revalidate'
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['X-Download-Options'] = 'noopen'
            response['X-Permitted-Cross-Domain-Policies'] = 'none'
            response['Referrer-Policy'] = 'no-referrer-when-downgrade'
            response['Clear-Site-Data'] = '"cache"'
            
        # 针对API响应的缓存控制
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, s-maxage=0'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
        return response