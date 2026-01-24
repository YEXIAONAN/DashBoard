import requests
import json

# django服务器地址
base_url = 'http://127.0.0.1:8000'

# 使用第一个用户进行登录
login_data = {
    'phone': '13800138000',
    'password': '123456'
}

# 创建一个session对象来维持cookie
session = requests.session()

try:
    # 首先获取页面以获取csrf token
    print('正在获取csrf token...')
    response = session.get(f'{base_url}/login/')
    
    # 从cookie中获取csrftoken
    csrf_token = session.cookies.get('csrftoken')
    if csrf_token:
        print(f'获取到csrf token: {csrf_token[:20]}...')
    else:
        print('未获取到csrf token')
    
    # 设置请求头
    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': f'{base_url}/login/'
    }
    
    # 发送登录请求
    print('正在发送登录请求...')
    response = session.post(
        f'{base_url}/api/login/', 
        json=login_data,
        headers=headers
    )
    
    print(f'登录响应状态码: {response.status_code}')
    print(f'登录响应内容: {response.text}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print('登录成功！')
            print('用户信息:', result.get('user'))
            
            # 测试访问repo页面
            print('\n正在测试访问repo页面...')
            repo_response = session.get(f'{base_url}/repo/')
            print(f'repo页面状态码: {repo_response.status_code}')
            
            if repo_response.status_code == 200:
                print('repo页面访问成功！')
                # 检查页面内容中是否包含个性化推荐菜单
                content = repo_response.text
                if '个性化推荐菜单' in content:
                    print('✓ 页面中包含"个性化推荐菜单"文本')
                else:
                    print('✗ 页面中不包含"个性化推荐菜单"文本')
                
                if '香辣虾' in content or '酸辣土豆丝' in content:
                    print('✓ 页面中包含推荐菜品')
                else:
                    print('✗ 页面中不包含推荐菜品')
                
                # 保存页面内容到文件以便检查
                with open('repo_page_content.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print('页面内容已保存到 repo_page_content.html')
            else:
                print(f'repo页面访问失败，状态码: {repo_response.status_code}')
        else:
            print(f'登录失败: {result.get("message")}')
    else:
        print(f'登录请求失败，状态码: {response.status_code}')
        print(f'响应内容: {response.text}')
        
except requests.exceptions.ConnectionError:
    print('无法连接到服务器，请确保django服务器正在运行')
except Exception as e:
    print(f'发生错误: {e}')