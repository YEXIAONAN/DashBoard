from django.core import serializers
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render

from django.template.defaultfilters import date
# 2. 定义所有页面的渲染视图
from django.utils import timezone
from .models import DishOrderTable, UserInputDishTable
from collections import defaultdict

from datetime import date, timedelta, datetime
from calendar import monthrange # 导入 monthrange 以获取月份天数

from .models import NutritionRecord # 确保这个导入是正确的

# --- 基本页面视图 ---
def index(request):
    # 1. 推荐菜品（最多 4 条）
    dishes = DishOrderTable.objects.all()[:4]

    # 2. 今日营养汇总
    today = timezone.localdate()
    totals = (
        UserInputDishTable.objects
        .filter(created_at__date=today)
        .aggregate(
            calorie=Coalesce(Sum('calorie'), Value(0), output_field=DecimalField()),
            protein=Coalesce(Sum('protein'), Value(0), output_field=DecimalField()),
            fat=Coalesce(Sum('fat'), Value(0), output_field=DecimalField()),
            carbohydrate=Coalesce(Sum('carbohydrate'), Value(0), output_field=DecimalField()),
            fiber=Coalesce(Sum('fiber'), Value(0), output_field=DecimalField()),
        )
    )

    return render(request, 'index.html', {
        'dishes': dishes,
        'today': today,
        'today_total': totals,
    })

def orders(request):
    # 查询所有菜品，传给模板
    dishes = DishOrderTable.objects.all()

    # 叶小楠Bug记录 ： 购物车无法显示总蛋白质问题
    # print(f"--- 调试信息: 正在渲染菜品 '{dishes[0].name}'，其蛋白质为: {dishes[0].total_protein} ---")
    return render(request, 'orders.html', {'dishes': dishes})

def profile(request):
    """
    渲染个人中心页面
    """
    return render(request, 'profile.html')

def order_history(request):
    cutoff = timezone.now() - timedelta(days=3)

    # ① 最近 3 天的订单记录
    dishes = UserInputDishTable.objects.filter(created_at__gte=cutoff)

    # ② 菜品名 → 图片 URL 映射
    img_map = {d.name: d.image_url for d in DishOrderTable.objects.all()}

    # ③ 按日期+菜品名聚合
    grouped = defaultdict(lambda: defaultdict(int))
    price_map, calorie_map, protein_map = {}, {}, {}
    for d in dishes:
        day = d.created_at.date()
        grouped[day][d.dishname] += 1
        price_map[d.dishname] = float(d.price)
        calorie_map[d.dishname] = float(d.calorie)
        protein_map[d.dishname] = float(d.protein)

    # ④ 整理模板数据
    history = []
    for day in sorted(grouped.keys(), reverse=True):
        dish_list = []
        for name, cnt in grouped[day].items():
            dish_list.append({
                'dishname': name,
                'count': cnt,
                'price': price_map[name],
                'calorie': calorie_map[name],
                'protein': protein_map[name],
                'subtotal': round(price_map[name] * cnt, 2),
                'image_url': img_map.get(name, 'Images/default.jpg'),
            })
        total = round(sum(d['subtotal'] for d in dish_list), 2)
        history.append({'day': day, 'dishes': dish_list, 'total': total})

    return render(request, 'order_history.html', {'history': history})

def nutrition_recipes(request):
    dishes = DishOrderTable.objects.all()  # 或者你用过滤条件
    return render(request, 'nutrition_recipes.html', {'dishes': dishes})

def repo(request):
    """
    渲染报告页面
    """
    return render(request, 'repo.html')


def MyOrder(request):
    cutoff = timezone.now() - timedelta(days=3)
    dishes = UserInputDishTable.objects.filter(created_at__gte=cutoff)

    img_map = {d.name: d.image_url for d in DishOrderTable.objects.all()}
    grouped = defaultdict(lambda: defaultdict(int))
    price_map, calorie_map, protein_map = {}, {}, {}
    for d in dishes:
        day = d.created_at.date()
        grouped[day][d.dishname] += 1
        price_map[d.dishname] = float(d.price)
        calorie_map[d.dishname] = float(d.calorie)
        protein_map[d.dishname] = float(d.protein)

    history = []
    for day in sorted(grouped.keys(), reverse=True):
        dish_list = []
        for name, cnt in grouped[day].items():
            dish_list.append({
                'dishname': name,
                'count': cnt,
                'price': price_map[name],
                'calorie': calorie_map[name],
                'protein': protein_map[name],
                'subtotal': round(price_map[name] * cnt, 2),
                'image_url': img_map.get(name, 'Images/default.jpg'),
            })
        total = round(sum(d['subtotal'] for d in dish_list), 2)
        history.append({'day': day, 'dishes': dish_list, 'total': total})

    # 假设模板中用到order，传递history或orders，模板变量保持一致
    return render(request, 'MyOrder.html', {'history': history})

def Collection(request):
    return render(request, 'Collection.html')

def NoComment(request):
    return render(request, 'NoComment.html')

def profile_view(request):
    return render(request, 'profile.html')  # 渲染 profile.html 模板

def menu_view(request):
    dishes = DishOrderTable.objects.all()  # 查询所有菜品
    return render(request, 'main/menu.html', {'dishes': dishes})


from django.http import JsonResponse
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from .models import NutritionRecord # 确保 NutritionRecord 模型已导入
from django.http import JsonResponse
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from .models import NutritionRecord # 确保 NutritionRecord 模型已导入

# 定义每日热量目标
DAILY_CALORIE_GOAL = 2000 # 设置热量目标为2000 kcal

def daily_summary_data(request):
    """
    获取本日的日均热量、对比昨日的增加/减少百分比，以及热量目标达成情况。
    """
    current_date_today = now().date()
    previous_date_yesterday = current_date_today - timedelta(days=1)

    # 获取今日总热量
    today_calories_aggregated_data = NutritionRecord.objects.filter(
        created_at__date=current_date_today
    ).aggregate(total_calories_for_today=Sum('calorie'))
    total_calories_consumed_today = float(today_calories_aggregated_data['total_calories_for_today'] or 0)

    # 获取昨日总热量
    yesterday_calories_aggregated_data = NutritionRecord.objects.filter(
        created_at__date=previous_date_yesterday
    ).aggregate(total_calories_for_yesterday=Sum('calorie'))
    total_calories_consumed_yesterday = float(yesterday_calories_aggregated_data['total_calories_for_yesterday'] or 0)

    # 计算日均热量（对于单日，就是当日总热量）
    calculated_daily_average_calories = total_calories_consumed_today

    # 计算日均热量对比昨日的变化百分比
    daily_calorie_change_percentage = 0
    if total_calories_consumed_yesterday > 0:
        daily_calorie_change_percentage = ((total_calories_consumed_today - total_calories_consumed_yesterday) / total_calories_consumed_yesterday) * 100
    elif total_calories_consumed_today > 0: # 昨日为0，今日有数据，视为大幅增长
        daily_calorie_change_percentage = 100 # 或者一个很大的正数，表示从无到有
    # 如果都为0，则变化为0

    # 计算今日热量目标达成百分比
    current_day_goal_achievement_percentage = 0
    if DAILY_CALORIE_GOAL > 0:
        current_day_goal_achievement_percentage = (total_calories_consumed_today / DAILY_CALORIE_GOAL) * 100

    # 计算昨日热量目标达成百分比
    previous_day_goal_achievement_percentage = 0
    if DAILY_CALORIE_GOAL > 0:
        previous_day_goal_achievement_percentage = (total_calories_consumed_yesterday / DAILY_CALORIE_GOAL) * 100

    # 计算热量目标达成对比昨日的变化百分比
    goal_achievement_comparison_percentage = 0
    if previous_day_goal_achievement_percentage > 0:
        goal_achievement_comparison_percentage = ((current_day_goal_achievement_percentage - previous_day_goal_achievement_percentage) / previous_day_goal_achievement_percentage) * 100
    elif current_day_goal_achievement_percentage > 0: # 昨日达成率为0，今日有达成，视为大幅增长
        goal_achievement_comparison_percentage = 100 # 或者一个很大的正数

    return JsonResponse({
        'daily_avg_calories': round(calculated_daily_average_calories, 2),
        'calorie_change_percentage': round(daily_calorie_change_percentage, 2),
        'daily_goal_achievement_percentage': round(current_day_goal_achievement_percentage, 2),
        'goal_achievement_change_percentage': round(goal_achievement_comparison_percentage, 2),
        'calorie_goal': DAILY_CALORIE_GOAL # 返回目标值，以备前端显示
    })








def calorie_trend_data(request):
    """
    获取用户最近两周的每日卡路里摄入趋势数据（本周和上周）。
    """
    today = now().date()

    # 计算本周的日期范围
    # current_weekday = today.weekday() # 0=Monday, 6=Sunday
    # current_week_start = today - timedelta(days=current_weekday)
    # current_week_end = current_week_start + timedelta(days=6)

    # 为了简化，我们直接获取最近7天作为“本周”，和再前7天作为“上周”
    # 这样可以避免复杂的周一到周日计算，更符合“最近一周”和“上一周”的直观理解
    # 如果严格需要周一到周日，请保留您原来的 current_weekday 计算逻辑

    # 获取本周数据 (最近7天)
    this_week_start = today - timedelta(days=6)
    this_week_end = today

    this_week_calorie_queryset = (
        NutritionRecord.objects
        .filter(created_at__date__range=[this_week_start, this_week_end])
        .values('created_at__date')
        .annotate(total_calories=Sum('calorie'))
        .order_by('created_at__date')
    )

    this_week_calorie_map = {
        entry['created_at__date'].strftime('%Y-%m-%d'): float(entry['total_calories'])
        for entry in this_week_calorie_queryset
    }

    # 获取上周数据 (再前7天)
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_end - timedelta(days=7)

    last_week_calorie_queryset = (
        NutritionRecord.objects
        .filter(created_at__date__range=[last_week_start, last_week_end])
        .values('created_at__date')
        .annotate(total_calories=Sum('calorie'))
        .order_by('created_at__date')
    )

    last_week_calorie_map = {
        entry['created_at__date'].strftime('%Y-%m-%d'): float(entry['total_calories'])
        for entry in last_week_calorie_queryset
    }

    x_data = [] # 日期标签
    this_week_data = [] # 本周每日卡路里
    last_week_data = [] # 上周每日卡路里

    # 填充过去14天的数据，以确保x_data和y_data的对齐
    # 这里我们只生成本周的x_data，因为折线图通常只需要一组日期轴
    for i in range(7):
        current_date_for_this_week = this_week_start + timedelta(days=i)
        date_str_this_week = current_date_for_this_week.strftime('%Y-%m-%d')
        x_data.append(date_str_this_week)

        # 获取本周数据，如果当天没有记录则为0
        calories_this_week = this_week_calorie_map.get(date_str_this_week, 0)
        this_week_data.append(round(calories_this_week, 2))

        # 获取上周对应日期的数据
        # 注意：上周的日期是 this_week_start - 7天 + i 天
        current_date_for_last_week = last_week_start + timedelta(days=i)
        date_str_last_week = current_date_for_last_week.strftime('%Y-%m-%d')
        calories_last_week = last_week_calorie_map.get(date_str_last_week, 0)
        last_week_data.append(round(calories_last_week, 2))


    return JsonResponse({
        'x_data': x_data,
        'this_week_data': this_week_data, # 重命名 y_data 为 this_week_data
        'last_week_data': last_week_data, # 新增上周数据
    })

def api_orders(request):
    orders = UserInputDishTable.objects.all().order_by('-created_at')

    data = [
        {
            'id': order.id,
            'username': order.name,
            'dishname': order.dishname,
            'price': str(order.price),
            'calorie': str(order.calorie),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for order in orders
    ]
    return JsonResponse(data, safe=False)

def nutrient_comparison_data(request):
    """
    提供 JSON 接口，供前端 AJAX 获取订单数据
    获取本周和上周的营养素（碳水、蛋白质、脂肪、膳食纤维、添加糖）总和数据。
    """
    today = now().date()

    current_weekday = today.weekday() # 0=Monday, 6=Sunday
    current_week_start = today - timedelta(days=current_weekday)
    current_week_end = current_week_start + timedelta(days=6)

    last_week_end = current_week_start - timedelta(days=1)
    last_week_start = last_week_end - timedelta(days=6)

    def get_nutrient_sums_for_week(start_date, end_date):
        data = NutritionRecord.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).aggregate(
            total_carbohydrate=Sum('carbohydrate'),
            total_protein=Sum('protein'),
            total_fat=Sum('fat'),
            total_fiber=Sum('fiber'),
            total_sugar_added=Sum('sugar_added'),
        )
        return {
            '碳水': float(data['total_carbohydrate'] or 0),
            '蛋白质': float(data['total_protein'] or 0),
            '脂肪': float(data['total_fat'] or 0),
            '膳食纤维': float(data['total_fiber'] or 0),
            '添加糖': float(data['total_sugar_added'] or 0),
        }

    this_week_data = get_nutrient_sums_for_week(current_week_start, current_week_end)
    last_week_data = get_nutrient_sums_for_week(last_week_start, last_week_end)

    labels = ['碳水', '蛋白质', '脂肪', '膳食纤维', '添加糖']
    this_week_values = [this_week_data[label] for label in labels]
    last_week_values = [last_week_data[label] for label in labels]

    return JsonResponse({
        'labels': labels,
        'this_week_data': this_week_values,
        'last_week_data': last_week_values,
    })

# --- 月报热量趋势折线图数据视图 ---

def get_weekly_calorie_sums_for_month(year, month):
    weekly_sums = []
    labels = []

    first_day_of_month = date(year, month, 1)
    last_day_of_month = date(year, month, monthrange(year, month)[1])

    current_week_start = first_day_of_month - timedelta(days=first_day_of_month.weekday())

    week_counter = 1
    while current_week_start <= last_day_of_month and week_counter <= 4:
        current_week_end = current_week_start + timedelta(days=6)

        query_start = max(current_week_start, first_day_of_month)
        query_end = min(current_week_end, last_day_of_month)

        total_calories = 0
        if query_start <= query_end:
            weekly_calories_agg = NutritionRecord.objects.filter(
                created_at__date__range=[query_start, query_end]
            ).aggregate(total_calories=Sum('calorie'))
            total_calories = float(weekly_calories_agg['total_calories'] or 0)

        weekly_sums.append(round(total_calories, 2))
        labels.append(f'第{week_counter}周')

        current_week_start += timedelta(days=7)
        week_counter += 1

    return labels, weekly_sums

def monthly_calorie_data(request):
    """
    获取本月和上月的每周热量趋势数据。
    """
    current_date = now().date()

# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Order, OrderItem, Dish
#
# @csrf_exempt
# def submit_order(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         items = data.get('items', [])
#         if not items:
#             return JsonResponse({'status': 'error', 'message': '购物车为空'})
#
#         order = Order.objects.create(user=request.user if request.user.is_authenticated else None)
#         total_price = 0
#         for item in items:
#             dish = Dish.objects.filter(name=item['name']).first()
#             if not dish:
#                 return JsonResponse({'status': 'error', 'message': f'菜品不存在：{item["name"]}'})
#             OrderItem.objects.create(
#                 order=order,
#                 dish=dish,
#                 quantity=item['quantity'],
#                 price=item['price']
#             )
#             total_price += item['price'] * item['quantity']
#         order.total_price = total_price
#         order.save()
#
#         return JsonResponse({'status': 'success', 'order_id': order.id})
    this_month_year = current_date.year
    this_month_month = current_date.month

    if this_month_month == 1:
        last_month_year = this_month_year - 1
        last_month_month = 12
    else:
        last_month_year = this_month_year
        last_month_month = this_month_month - 1

    this_month_labels, this_month_data = get_weekly_calorie_sums_for_month(this_month_year, this_month_month)
    last_month_labels, last_month_data = get_weekly_calorie_sums_for_month(last_month_year, last_month_month)

    max_weeks = max(len(this_month_labels), len(last_month_labels))

    while len(this_month_data) < max_weeks:
        this_month_data.append(0)
    while len(last_month_data) < max_weeks:
        last_month_data.append(0)

    final_labels = [f'第{i+1}周' for i in range(max_weeks)]

    return JsonResponse({
        'labels': final_labels,
        'this_month_data': this_month_data,
        'last_month_data': last_month_data,
    })

# --- 月报概览数据视图 ---
def monthly_summary_data(request):
    """
    获取月报概览数据，包含以下关键指标：
    - 本月日期范围
    - 月均摄入热量及与上月对比
    - 热量目标达成百分比及变化
    - 健康指数及变化
    - 月度热量缺口及变化
    - 多种营养素摄入数据及趋势对比
    """
    current_date = now().date()

    # 当前月份的起始和结束日期
    this_month_year = current_date.year
    this_month_month = current_date.month
    this_month_start = date(this_month_year, this_month_month, 1)
    this_month_end = date(this_month_year, this_month_month, monthrange(this_month_year, this_month_month)[1])

    # 上一个月份的起始和结束日期
    if this_month_month == 1:
        last_month_year = this_month_year - 1
        last_month_month = 12
    else:
        last_month_year = this_month_year
        last_month_month = this_month_month - 1
    last_month_start = date(last_month_year, last_month_month, 1)
    last_month_end = date(last_month_year, last_month_month, monthrange(last_month_year, last_month_month)[1])

    # 每日营养目标值定义
    daily_calorie_goal = 1500  # 每日热量目标(kcal)
    daily_protein_goal = 60    # 每日蛋白质目标(g)
    daily_fiber_goal = 25     # 每日膳食纤维目标(g)
    daily_calcium_goal = 800   # 每日钙目标(mg)
    daily_vitamin_c_goal = 100 # 每日维生素C目标(mg)
    daily_fat_limit = 70       # 每日脂肪限制(g)

    daily_sugar_added_limit = 25 # 每日添加糖限制(g)
    
    # TDEE（总日常能量消耗）计算 - 基于平均成人估计
    # 可以根据用户实际信息调整这些参数
    user_age = 30  # 假设用户年龄
    user_weight = 65  # 假设用户体重(kg)
    user_height = 170  # 假设用户身高(cm)
    user_gender = 'female'  # 假设性别
    activity_level = 1.375  # 轻度活动水平
    
    # 计算BMR（基础代谢率）
    if user_gender == 'male':
        bmr = 88.362 + (13.397 * user_weight) + (4.799 * user_height) - (5.677 * user_age)
    else:
        bmr = 447.593 + (9.247 * user_weight) + (3.098 * user_height) - (4.330 * user_age)
    
    # 计算TDEE
    tdee = bmr * activity_level

    def get_monthly_aggregated_data(start_date, end_date, current_month_flag=True):
        """
        辅助函数：聚合指定月份的的营养数据
        参数:
            start_date: 月份起始日期
            end_date: 月份结束日期
            current_month_flag: 是否为当前月份(影响数据计算范围)
        返回:
            包含各类营养指标聚合结果的字典
        """
        query_end_date = min(end_date, current_date) if current_month_flag else end_date

        records = NutritionRecord.objects.filter(
            created_at__date__range=[start_date, query_end_date]
        ).aggregate(
            total_calories=Sum('calorie'),
            total_protein=Sum('protein'),
            total_fiber=Sum('fiber'),
            total_calcium=Sum('calcium'),
            total_vitamin_c=Sum('vitamin_c'),
            total_fat=Sum('fat'),
            total_sugar_added=Sum('sugar_added'),
        )

        daily_records = NutritionRecord.objects.filter(
            created_at__date__range=[start_date, query_end_date]
        ).values('created_at__date').annotate(
            day_calories=Sum('calorie'),
            day_protein=Sum('protein'),
            day_fiber=Sum('fiber'),
            day_calcium=Sum('calcium'),
            day_vitamin_c=Sum('vitamin_c'),
            day_fat=Sum('fat'),
            day_sugar_added=Sum('sugar_added'),
        ).order_by('created_at__date')

        total_calories = 0
        total_protein = 0
        total_fiber = 0
        total_calcium = 0
        total_vitamin_c = 0
        total_fat = 0
        total_sugar_added = 0

        days_with_records = 0
        days_goal_achieved = 0
        accumulated_deficit_kcal = 0

        for entry in daily_records:
            days_with_records += 1

            day_cal = float(entry['day_calories'] or 0)
            day_protein = float(entry['day_protein'] or 0)
            day_fiber = float(entry['day_fiber'] or 0)
            day_calcium = float(entry['day_calcium'] or 0)
            day_vitamin_c = float(entry['day_vitamin_c'] or 0)
            day_fat = float(entry['day_fat'] or 0)
            day_sugar_added = float(entry['day_sugar_added'] or 0)

            total_calories += day_cal
            total_protein += day_protein
            total_fiber += day_fiber
            total_calcium += day_calcium
            total_vitamin_c += day_vitamin_c
            total_fat += day_fat
            total_sugar_added += day_sugar_added

            # 使用TDEE计算每日热量缺口
            daily_deficit = tdee - day_cal
            accumulated_deficit_kcal += daily_deficit

            if day_cal <= daily_calorie_goal:
                days_goal_achieved += 1

        if current_month_flag:
            total_days_in_period = (query_end_date - start_date).days + 1
        else:
            total_days_in_period = (end_date - start_date).days + 1

        monthly_avg_calories = round(total_calories / total_days_in_period, 2) if total_days_in_period > 0 else 0

        # 计算月度TDEE总量
        monthly_tdee_total = tdee * total_days_in_period
        monthly_goal_achievement_percentage = round((total_calories / monthly_tdee_total) * 100, 2) if monthly_tdee_total > 0 else 0

        health_score = 0
        if days_with_records > 0:
            avg_protein = total_protein / days_with_records
            avg_fiber = total_fiber / days_with_records
            avg_sugar_added = total_sugar_added / days_with_records
            avg_fat = total_fat / days_with_records

            protein_score = min(avg_protein / daily_protein_goal, 1.5) * 30
            fiber_score = min(avg_fiber / daily_fiber_goal, 1.5) * 30

            sugar_score = max(0, 1 - (avg_sugar_added / daily_sugar_added_limit)) * 20
            fat_score = max(0, 1 - (avg_fat / daily_fat_limit)) * 20

            health_score = round(protein_score + fiber_score + sugar_score + fat_score, 2)
            health_score = min(max(health_score, 0), 100)

        new_dishes_tried = 0
        if current_month_flag:
            new_dishes_tried = 12
        else:
            new_dishes_tried = 10

        avg_fiber_intake = round(total_fiber / days_with_records, 2) if days_with_records > 0 else 0
        avg_fat_intake = round(total_fat / days_with_records, 2) if days_with_records > 0 else 0
        avg_calcium_intake = round(total_calcium / days_with_records, 2) if days_with_records > 0 else 0
        avg_vitamin_c_intake = round(total_vitamin_c / days_with_records, 2) if days_with_records > 0 else 0

        calcium_goal_achievement_percentage = round((avg_calcium_intake / daily_calcium_goal) * 100, 2) if daily_calcium_goal > 0 else 0

        return {
            'total_calories': total_calories,
            'monthly_avg_calories': monthly_avg_calories,
            'monthly_goal_achievement_percentage': monthly_goal_achievement_percentage,
            'health_index': health_score,
            'new_dishes_tried': new_dishes_tried,
            'monthly_calorie_deficit_kcal': round(max(0, monthly_tdee_total - total_calories), 2),
            'days_goal_achieved': days_goal_achieved,
            'avg_fiber_intake': avg_fiber_intake,
            'avg_fat_intake': avg_fat_intake,
            'avg_calcium_intake': avg_calcium_intake,
            'avg_vitamin_c_intake': avg_vitamin_c_intake,
            'calcium_goal_achievement_percentage': calcium_goal_achievement_percentage,
        }

    this_month_data = get_monthly_aggregated_data(this_month_start, this_month_end, current_month_flag=True)
    last_month_data = get_monthly_aggregated_data(last_month_start, last_month_end, current_month_flag=False)

    def calculate_change(current_val, previous_val):
        if previous_val == 0:
            return 100 if current_val > 0 else 0
        return round(((current_val - previous_val) / previous_val) * 100, 2)

    avg_calorie_change = calculate_change(this_month_data['monthly_avg_calories'], last_month_data['monthly_avg_calories'])
    goal_achievement_change = calculate_change(this_month_data['monthly_goal_achievement_percentage'], last_month_data['monthly_goal_achievement_percentage'])
    health_index_change = calculate_change(this_month_data['health_index'], last_month_data['health_index'])
    new_dishes_change = calculate_change(this_month_data['new_dishes_tried'], last_month_data['new_dishes_tried'])
    monthly_deficit_change = calculate_change(this_month_data['monthly_calorie_deficit_kcal'], last_month_data['monthly_calorie_deficit_kcal'])
    days_goal_achieved_change = calculate_change(this_month_data['days_goal_achieved'], last_month_data['days_goal_achieved'])
    fiber_intake_change = calculate_change(this_month_data['avg_fiber_intake'], last_month_data['avg_fiber_intake'])
    fat_intake_change = calculate_change(this_month_data['avg_fat_intake'], last_month_data['avg_fat_intake'])
    calcium_goal_change = calculate_change(this_month_data['calcium_goal_achievement_percentage'], last_month_data['calcium_goal_achievement_percentage'])
    vitamin_c_intake_change = calculate_change(this_month_data['avg_vitamin_c_intake'], last_month_data['avg_vitamin_c_intake'])

    return JsonResponse({
        'this_month_start_date': this_month_start.strftime('%#m月%#d日'),
        'this_month_end_date': this_month_end.strftime('%#m月%#d日'),
        'monthly_avg_calories': this_month_data['monthly_avg_calories'],
        'avg_calorie_change': avg_calorie_change,
        'monthly_goal_achievement_percentage': this_month_data['monthly_goal_achievement_percentage'],
        'goal_achievement_change': goal_achievement_change,
        'health_index': this_month_data['health_index'], # 这里返回实际值，前端再决定如何显示
        'health_index_change': health_index_change, # 这里返回变化量
        'new_dishes_tried': this_month_data['new_dishes_tried'],
        'new_dishes_change': new_dishes_change,
        'monthly_calorie_deficit_kcal': this_month_data['monthly_calorie_deficit_kcal'],
        'monthly_deficit_change': monthly_deficit_change,
        'days_goal_achieved': this_month_data['days_goal_achieved'],
        'days_goal_achieved_change': days_goal_achieved_change,
        'fiber_intake_this_month': this_month_data['avg_fiber_intake'],
        'fiber_intake_change': fiber_intake_change,
        'fat_intake_this_month': this_month_data['avg_fat_intake'],
        'fat_intake_change': fat_intake_change,
        'calcium_goal_achievement_this_month': this_month_data['calcium_goal_achievement_percentage'],
        'calcium_goal_change': calcium_goal_change,
        'vitamin_c_intake_this_month': this_month_data['avg_vitamin_c_intake'],
        'vitamin_c_change': vitamin_c_intake_change, # 修正变量名以保持一致性
    })



# --- 新增：周报营养素分析数据视图 ---

def get_weekly_nutrient_analysis_raw_data(start_date, end_date, current_date_limit=None):
    """
    辅助函数：获取指定日期范围内的营养素和卡路里汇总数据。
    current_date_limit 用于确保对本周的查询只到当前日期。
    """
    query_end_date = min(end_date, current_date_limit) if current_date_limit else end_date

    records = NutritionRecord.objects.filter(created_at__date__range=[start_date, query_end_date])

    # 聚合总营养素和卡路里
    aggregated_data = records.aggregate(
        total_calories=Sum('calorie'),
        total_carbohydrate=Sum('carbohydrate'),
        total_protein=Sum('protein'),
        total_fat=Sum('fat'),
        total_sugar_added=Sum('sugar_added'),
    )

    # 计算该时间段内有记录的天数
    days_with_records = records.values('created_at__date').distinct().count()

    return {
        'total_calories': float(aggregated_data['total_calories'] or 0),
        'total_carbohydrate': float(aggregated_data['total_carbohydrate'] or 0),
        'total_protein': float(aggregated_data['total_protein'] or 0),
        'total_fat': float(aggregated_data['total_fat'] or 0),
        'total_sugar_added': float(aggregated_data['total_sugar_added'] or 0),
        'days_with_records': days_with_records,
    }

def weekly_nutrient_analysis_data(request):
    """
    获取周报营养素分析数据：
    - 碳水、蛋白质、脂肪的能量占比及与上周对比
    - 日均添加糖摄入量及与上周对比
    """
    today = now().date()

    # 计算本周 (周一到周日)
    current_weekday = today.weekday() # 0=周一, 6=周日
    this_week_start = today - timedelta(days=current_weekday)
    this_week_end = this_week_start + timedelta(days=6)

    # 计算上周 (上周一到上周日)
    last_week_end = this_week_start - timedelta(days=1)
    last_week_start = last_week_end - timedelta(days=6)

    # 获取本周和上周的原始数据
    this_week_raw_data = get_weekly_nutrient_analysis_raw_data(this_week_start, this_week_end, current_date_limit=today)
    last_week_raw_data = get_weekly_nutrient_analysis_raw_data(last_week_start, last_week_end)

    # 辅助函数：计算宏量营养素的能量占比
    def calculate_macro_percentages(data):
        total_carb_cal = data['total_carbohydrate'] * 4
        total_protein_cal = data['total_protein'] * 4
        total_fat_cal = data['total_fat'] * 9

        # 使用数据库中的总热量，如果为0则使用宏量营养素计算的总热量
        total_calories_for_percent = data['total_calories']
        if total_calories_for_percent == 0:
            total_calories_for_percent = total_carb_cal + total_protein_cal + total_fat_cal
            if total_calories_for_percent == 0: # 避免除以零
                return {'carb_percent': 0, 'protein_percent': 0, 'fat_percent': 0}

        carb_percent = round((total_carb_cal / total_calories_for_percent) * 100, 2)
        protein_percent = round((total_protein_cal / total_calories_for_percent) * 100, 2)
        fat_percent = round((total_fat_cal / total_calories_for_percent) * 100, 2)

        return {
            'carb_percent': carb_percent,
            'protein_percent': protein_percent,
            'fat_percent': fat_percent,
        }

    # 计算本周和上周的百分比
    this_week_percentages = calculate_macro_percentages(this_week_raw_data)
    last_week_percentages = calculate_macro_percentages(last_week_raw_data)

    # 计算日均添加糖
    this_week_avg_sugar_added = round(this_week_raw_data['total_sugar_added'] / this_week_raw_data['days_with_records'], 2) if this_week_raw_data['days_with_records'] > 0 else 0
    last_week_avg_sugar_added = round(last_week_raw_data['total_sugar_added'] / last_week_raw_data['days_with_records'], 2) if last_week_raw_data['days_with_records'] > 0 else 0

    # 辅助函数：计算变化百分比
    def calculate_change(current_val, previous_val):
        if previous_val == 0:
            return 100 if current_val > 0 else 0 # 如果上周为0，本周有值，则视为100%增长
        return round(((current_val - previous_val) / previous_val) * 100, 2)

    # 计算各项变化
    carb_percent_change = calculate_change(this_week_percentages['carb_percent'], last_week_percentages['carb_percent'])
    protein_percent_change = calculate_change(this_week_percentages['protein_percent'], last_week_percentages['protein_percent'])
    fat_percent_change = calculate_change(this_week_percentages['fat_percent'], last_week_percentages['fat_percent'])
    avg_sugar_added_change = calculate_change(this_week_avg_sugar_added, last_week_avg_sugar_added)

    return JsonResponse({
        'this_week_carb_percent': this_week_percentages['carb_percent'],
        'carb_percent_change': carb_percent_change,
        'this_week_protein_percent': this_week_percentages['protein_percent'],
        'protein_percent_change': protein_percent_change,
        'this_week_fat_percent': this_week_percentages['fat_percent'],
        'fat_percent_change': fat_percent_change,
        'this_week_avg_sugar_added': this_week_avg_sugar_added,
        'avg_sugar_added_change': avg_sugar_added_change,
    })


# --- 周报概览数据视图 ---
def weekly_summary_data(request):
    """
    获取周报概览数据：
    - 本周日期范围
    - 日均摄入热量及与昨日对比
    - 热量目标达成百分比 (目标：1500 kcal)
    - 本周热量缺口累积 (kg)
    """
    today = now().date()
    yesterday = today - timedelta(days=1)

    current_weekday = today.weekday() # 0=周一, 6=周日
    week_start = today - timedelta(days=current_weekday) # 本周一
    week_end = week_start + timedelta(days=6) # 本周日

    today_calories_agg = NutritionRecord.objects.filter(created_at__date=today).aggregate(total_calories=Sum('calorie'))
    today_total_calories = float(today_calories_agg['total_calories'] or 0)

    yesterday_calories_agg = NutritionRecord.objects.filter(created_at__date=yesterday).aggregate(total_calories=Sum('calorie'))
    yesterday_total_calories = float(yesterday_calories_agg['total_calories'] or 0)

    weekly_total_calories_agg = NutritionRecord.objects.filter(
        created_at__date__range=[week_start, today]
    ).aggregate(total_calories=Sum('calorie'))
    weekly_total_calories = float(weekly_total_calories_agg['total_calories'] or 0)

    days_in_week_so_far = (today - week_start).days + 1
    daily_avg_calories = round(weekly_total_calories / days_in_week_so_far, 2) if days_in_week_so_far > 0 else 0

    change_percentage = 0
    if yesterday_total_calories > 0:
        change_percentage = round(((today_total_calories - yesterday_total_calories) / yesterday_total_calories) * 100, 2)
    elif today_total_calories > 0:
        change_percentage = 100

    calorie_goal_per_day = 1500
    goal_achievement_percentage = round((today_total_calories / calorie_goal_per_day) * 100, 2) if calorie_goal_per_day > 0 else 0

    accumulated_deficit_kcal = 0
    for i in range(days_in_week_so_far):
        current_day = week_start + timedelta(days=i)
        day_calories_agg = NutritionRecord.objects.filter(created_at__date=current_day).aggregate(total_calories=Sum('calorie'))
        day_total_calories = float(day_calories_agg['total_calories'] or 0)
        accumulated_deficit_kcal += (calorie_goal_per_day - day_total_calories)

    accumulated_deficit_kg = round(accumulated_deficit_kcal / 7700, 2)

    return JsonResponse({
        'week_start_date': week_start.strftime('%#m月%#d日'),
        'week_end_date': week_end.strftime('%#m月%#d日'),
        'daily_avg_calories': daily_avg_calories,
        'today_total_calories': today_total_calories,
        'change_percentage': change_percentage,
        'goal_achievement_percentage': goal_achievement_percentage,
        'accumulated_deficit_kg': accumulated_deficit_kg,
    })





#月报雷达图营养数据视图
from .models import NutritionRecord
from django.db.models import Avg
from django.utils.timezone import now

def get_nutrient_radar_data(request):
    today = now()
    last_month = today.replace(day=1) - timedelta(days=1)

    this_month_avg = NutritionRecord.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month
    ).aggregate(
        protein=Avg('protein'),
        fiber=Avg('fiber'),
        calcium=Avg('calcium'),
        vitamin_c=Avg('vitamin_c'),
        iron=Avg('iron'),
        fat=Avg('fat')
    )

    last_month_avg = NutritionRecord.objects.filter(
        created_at__year=last_month.year,
        created_at__month=last_month.month
    ).aggregate(
        protein=Avg('protein'),
        fiber=Avg('fiber'),
        calcium=Avg('calcium'),
        vitamin_c=Avg('vitamin_c'),
        iron=Avg('iron'),
        fat=Avg('fat')
    )

    def safe(x):
        return round(x or 0, 2)

    return JsonResponse({
        "this_month": [safe(this_month_avg[k]) for k in ['protein', 'fiber', 'calcium', 'vitamin_c', 'iron', 'fat']],
        "last_month": [safe(last_month_avg[k]) for k in ['protein', 'fiber', 'calcium', 'vitamin_c', 'iron', 'fat']]
    })


#获取所有菜品信息为对象存入map字典中
def get_dish_name_map():

    dish_all = DishOrderTable.objects.all()

    dish_map = {dish.name: dish for dish in dish_all}

    return dish_map


#获取订单状态
def get_order_status(request):
    # 将字符串转换为带时区的 datetime 对象（假设原时间是当前时区）
    naive_time = datetime.strptime("2025-07-20 03:55:01", "%Y-%m-%d %H:%M:%S")
    aware_time = timezone.make_aware(naive_time, timezone.get_current_timezone())
    order_all = UserInputDishTable.objects.filter(created_at=aware_time)
    # progress = {
    #     # 'status': order.status,
    #     'data': order_all,
    #     # 'estimated_time': order.estimated_completion_time()
    # }
    #JsonResponse(progress)
    #序列化json
    data = serializers.serialize('json',order_all)

    return render(request, 'order_status.html', {'data': order_all})