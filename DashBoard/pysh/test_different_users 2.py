import requests
import json

# 测试不同用户的个性化推荐

def test_personalized_recommendations():
    base_url = "http://127.0.0.1:8000"
    
    # 测试用户1 - 董大 (user_id=1)
    print("=== 测试用户1: 董大 (user_id=1) ===")
    session1 = requests.Session()
    
    # 获取登录页面和CSRF token
    login_response = session1.get(f"{base_url}/login/")
    csrf_token = session1.cookies.get('csrftoken')
    
    # 登录用户1
    login_data = {
        'username': '董大',
        'password': '123456',
        'csrfmiddlewaretoken': csrf_token
    }
    login_result = session1.post(f"{base_url}/login/", data=login_data)
    print(f"用户1登录状态码: {login_result.status_code}")
    
    # 访问repo页面获取推荐
    repo_response = session1.get(f"{base_url}/repo/")
    print(f"用户1repo页面状态码: {repo_response.status_code}")
    
    if repo_response.status_code == 200:
        content = repo_response.text
        # 查找个性化推荐菜单部分
        if "个性化推荐菜单" in content:
            print("用户1的推荐菜品:")
            # 提取菜品名称
            import re
            dish_pattern = r'<div class="menu-name">([^<]+)</div>'
            dishes = re.findall(dish_pattern, content)
            for i, dish in enumerate(dishes[:4], 1):
                print(f"  {i}. {dish}")
        else:
            print("未找到个性化推荐菜单")
    
    print("\n" + "="*50 + "\n")
    
    # 测试用户2 - 假设有另一个用户
    print("=== 测试用户2: 假设用户 (user_id=2) ===")
    session2 = requests.Session()
    
    # 获取登录页面和CSRF token
    login_response2 = session2.get(f"{base_url}/login/")
    csrf_token2 = session2.cookies.get('csrftoken')
    
    # 尝试登录用户2 (这里可能需要根据实际数据库中的用户调整)
    login_data2 = {
        'username': 'testuser',  # 假设的用户名
        'password': '123456',
        'csrfmiddlewaretoken': csrf_token2
    }
    login_result2 = session2.post(f"{base_url}/login/", data=login_data2)
    print(f"用户2登录状态码: {login_result2.status_code}")
    
    # 如果登录成功，获取推荐
    if login_result2.status_code == 200:
        repo_response2 = session2.get(f"{base_url}/repo/")
        print(f"用户2repo页面状态码: {repo_response2.status_code}")
        
        if repo_response2.status_code == 200:
            content2 = repo_response2.text
            if "个性化推荐菜单" in content2:
                print("用户2的推荐菜品:")
                dish_pattern = r'<div class="menu-name">([^<]+)</div>'
                dishes2 = re.findall(dish_pattern, content2)
                for i, dish in enumerate(dishes2[:4], 1):
                    print(f"  {i}. {dish}")
            else:
                print("未找到个性化推荐菜单")
    else:
        print("用户2登录失败，可能用户不存在")
    
    print("\n" + "="*50 + "\n")
    
    # 检查数据库中的用户数据
    print("=== 检查数据库用户数据 ===")
    try:
        import django
        from django.conf import settings
        
        # 设置Django环境
        if not settings.configured:
            settings.configure(DEBUG=True)
            django.setup()
        
        from main.models import Users
        
        # 获取所有用户
        users = Users.objects.all()[:5]  # 只显示前5个用户
        print(f"数据库中的用户:")
        for user in users:
            bmi = user.weight / (user.height ** 2) if user.height and user.weight else 0
            bmi_category = '偏瘦' if bmi < 18.5 else '正常' if 18.5 <= bmi < 24.9 else '超重'
            print(f"  用户ID: {user.user_id}, 姓名: {user.name}, 身高: {user.height}m, 体重: {user.weight}kg")
            print(f"    BMI: {bmi:.1f}, 分类: {bmi_category}")
            print(f"    过敏史: {user.allergens or '无'}")
            print(f"    慢性疾病: {user.chronic_diseases or '无'}")
            print()
            
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    test_personalized_recommendations()