import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DashBoard.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from main.models import Users, Dishes
from main.views import personalized, getUserSession
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

def test_orders_recommendation():
    print("=== 测试订单页面个性化推荐功能 ===")
    
    # 获取测试用户
    users = Users.objects.all()[:2]
    
    if not users.exists():
        print("数据库中没有用户数据")
        return
    
    factory = RequestFactory()
    
    for user in users:
        print(f"\n--- 测试用户 {user.user_id}: {user.name or '未知'} ---")
        
        # 创建请求并设置会话
        request = factory.get('/orders/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        # 模拟用户登录
        request.session['user'] = {
            'user_id': user.user_id,
            'name': user.name,
            'phone': user.phone
        }
        request.session.save()
        
        # 测试个性化推荐
        try:
            recommendations = personalized(user.user_id)
            
            if recommendations and len(recommendations) > 0:
                dish_ids = recommendations[0].get("dish_id_arr", [])
                if dish_ids:
                    recommended_dishes = Dishes.objects.filter(dish_id__in=dish_ids)[:1]
                    if recommended_dishes.exists():
                        dish = recommended_dishes.first()
                        reason = recommendations[0].get('推荐理由', '根据您的健康数据智能推荐')
                        print(f"推荐菜品: {dish.name}")
                        print(f"推荐理由: {reason}")
                        print(f"热量: {dish.total_calorie} kcal, 蛋白质: {dish.total_protein}g")
                        print("✅ 个性化推荐成功")
                    else:
                        print("❌ 未找到推荐的菜品")
                else:
                    print("❌ 推荐菜品ID列表为空")
            else:
                print("❌ 个性化推荐失败")
                
        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_orders_recommendation()