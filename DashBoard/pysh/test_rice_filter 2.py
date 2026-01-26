import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DashBoard.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from main.models import Users, Dishes
from main.views import personalized

def test_rice_filter():
    print("=== 测试米饭过滤功能 ===")
    
    # 获取第一个用户
    user = Users.objects.first()
    
    if not user:
        print("数据库中没有用户数据")
        return
    print(f"测试用户: {user.user_id} ({user.name or '未知'})")
    
    # 获取个性化推荐
    try:
        recommendations = personalized(user.user_id)
        
        if recommendations and len(recommendations) > 0:
            dish_ids = recommendations[0].get("dish_id_arr", [])
            if dish_ids:
                # 获取推荐的菜品详细信息
                recommended_dishes = Dishes.objects.filter(dish_id__in=dish_ids)
                dish_names = [dish.name for dish in recommended_dishes]
                
                # 检查是否有米饭类菜品
                rice_keywords = ['米饭', '炒饭', '黄焖鸡米饭', '蛋炒饭', '虾仁炒饭']
                rice_dishes = [dish for dish in recommended_dishes if any(keyword in dish.name for keyword in rice_keywords)]
                
                print(f"\n推荐菜品数量: {len(recommended_dishes)}")
                print(f"推荐菜品列表:")
                for i, dish in enumerate(recommended_dishes, 1):
                    print(f"  {i}. {dish.name}")
                
                print(f"\n米饭类菜品检查:")
                print(f"包含米饭的菜品数量: {len(rice_dishes)}")
                
                if len(rice_dishes) > 0:
                    print("❌ 发现以下米饭类菜品:")
                    for dish in rice_dishes:
                        print(f"  - {dish.name}")
                else:
                    print("✅ 成功过滤掉所有米饭类菜品!")
                    
            else:
                print("没有推荐菜品")
        else:
            print("个性化推荐失败")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rice_filter()