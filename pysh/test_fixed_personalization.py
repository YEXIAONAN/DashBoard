import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DashBoard.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from main.models import Users, Dishes
from main.views import personalized

def test_personalization():
    print("=== 测试修复后的个性化推荐功能 ===")
    
    # 获取前3个用户
    users = Users.objects.all()[:3]
    
    if not users.exists():
        print("数据库中没有用户数据")
        return
    
    for user in users:
        print(f"\n--- 用户 {user.user_id}: {user.name or '未知'} ---")
        
        # 显示用户基本信息
        bmi = user.weight / (user.height ** 2) if user.height and user.weight else 0
        bmi_category = '偏瘦' if bmi < 18.5 else '正常' if 18.5 <= bmi < 24.9 else '超重'
        print(f"身高: {user.height}m, 体重: {user.weight}kg")
        print(f"BMI: {bmi:.1f}, 分类: {bmi_category}")
        print(f"过敏史: {user.allergens or '无'}")
        print(f"慢性疾病: {user.chronic_diseases or '无'}")
        
        # 获取个性化推荐
        try:
            recommendations = personalized(user.user_id)
            
            if recommendations and len(recommendations) > 0:
                dish_ids = recommendations[0].get("dish_id_arr", [])
                if dish_ids:
                    # 获取推荐的菜品详细信息
                    recommended_dishes = Dishes.objects.filter(dish_id__in=dish_ids)[:4]
                    dish_names = [dish.name for dish in recommended_dishes]
                    print(f"推荐菜品: {', '.join(dish_names)}")
                    print(f"推荐理由: {recommendations[0].get('推荐理由', '无')}")
                else:
                    print("没有推荐菜品")
            else:
                print("个性化推荐失败")
                
        except Exception as e:
            print(f"获取推荐时出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_personalization()