import requests
import json

# django服务器地址
base_url = 'http://127.0.0.1:8000'

# 使用第一个用户进行登录（从users.csv中获取）
login_data = {
    'phone': '13800138000',
    'password': '123456'  # 假设密码是123456
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
        print('未获取到csrf token，尝试从页面中提取...')
        # 尝试从页面内容中提取csrf token
        from bs4 import beautifulsoup
        soup = beautifulsoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f'从页面提取到csrf token: {csrf_token[:20]}...')
    
    # 设置请求头
    headers = {
        'x-csrftoken': csrf_token,
        'referer': f'{base_url}/login/'
    }
    
    # 发送登录请求
    print('正在发送登录请求...')
    response = session.post(
        f'{base_url}/api/login/', 
        json=login_data,
        headers=headers
    )
    
    print(f'响应状态码: {response.status_code}')
    print(f'响应内容: {response.text}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print('登录成功！')
            print('用户信息:', result.get('user'))
            
            # 获取session cookie
            session_cookie = session.cookies.get('sessionid')
            if session_cookie:
                print(f'session id: {session_cookie}')
            else:
                print('未获取到session cookie')
                
            # 测试获取聊天记录
            print('\n正在测试获取聊天记录...')
            chat_response = session.get(f'{base_url}/api/get_chat_history/')
            print(f'聊天记录响应状态码: {chat_response.status_code}')
            print(f'聊天记录响应内容: {chat_response.text}')
            
            # 测试保存聊天记录
            print('\n正在测试保存聊天记录...')
            test_message = {'message': '你好，这是一个测试消息', 'is_user': True}
            save_response = session.post(f'{base_url}/api/save_chat_message/', json=test_message)
            print(f'保存聊天记录响应状态码: {save_response.status_code}')
            print(f'保存聊天记录响应内容: {save_response.text}')
            
            # 再次获取聊天记录
            print('\n再次获取聊天记录...')
            chat_response2 = session.get(f'{base_url}/api/get_chat_history/')
            print(f'聊天记录响应状态码: {chat_response2.status_code}')
            print(f'聊天记录响应内容: {chat_response2.text}')
        else:
            print(f'登录失败: {result.get("message")}')
    else:
        print(f'请求失败，状态码: {response.status_code}')
        print(f'响应内容: {response.text}')
        
except requests.exceptions.connectionerror:
    print('无法连接到服务器，请确保django服务器正在运行')
except exception as e:
    print(f'发生错误: {e}')