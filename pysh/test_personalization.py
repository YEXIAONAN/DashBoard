import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oc_c.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from main.models import Users, Dishes
from main.views import personalized

def test_personalization_for_different_users():
    print("=== 测试不同用户的个性化推荐 ===")
    
    # 获取前5个用户
    users = Users.objects.all()[:5]
    
    if not users.exists():
        print("数据库中没有用户数据")
        return
    
    user_recommendations = {}
    
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
                    user_recommendations[user.user_id] = dish_names
                    print(f"推荐菜品: {', '.join(dish_names)}")
                    print(f"推荐理由: {recommendations[0].get('推荐理由', '无')}")
                else:
                    print("没有推荐菜品")
                    user_recommendations[user.user_id] = []
            else:
                print("个性化推荐失败")
                user_recommendations[user.user_id] = []
                
        except Exception as e:
            print(f"获取推荐时出错: {e}")
            user_recommendations[user.user_id] = []
    
    # 比较不同用户的推荐结果
    print("\n" + "="*60)
    print("=== 推荐结果比较 ===")
    
    all_recommendations = list(user_recommendations.values())
    
    if len(all_recommendations) > 1:
        # 检查是否有用户得到相同的推荐
        unique_recommendations = []
        duplicate_count = 0
        
        for i, recs in enumerate(all_recommendations):
            if recs in all_recommendations[:i]:
                duplicate_count += 1
                print(f"用户 {list(user_recommendations.keys())[i]} 的推荐与其他用户重复")
            else:
                unique_recommendations.append(recs)
        
        print(f"\n统计结果:")
        print(f"总用户数: {len(users)}")
        print(f"唯一推荐组合数: {len(unique_recommendations)}")
        print(f"重复推荐数: {duplicate_count}")
        
        if len(unique_recommendations) == len(users):
            print("✅ 每个用户都得到了不同的推荐！")
        elif len(unique_recommendations) > 1:
            print("⚠️  部分用户得到了不同的推荐，但存在重复")
        else:
            print("❌ 所有用户都得到了相同的推荐")
    else:
        print("只有一个用户，无法比较推荐差异")
    
    # 显示详细的推荐对比
    print("\n" + "="*60)
    print("=== 详细推荐对比 ===")
    for user_id, recommendations in user_recommendations.items():
        user = Users.objects.get(user_id=user_id)
        print(f"用户 {user_id} ({user.name or '未知'}): {recommendations}")

if __name__ == "__main__":
    test_personalization_for_different_users()