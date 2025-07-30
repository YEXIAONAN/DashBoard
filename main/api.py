# main/api.py

import json
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt  # <--- 导入 csrf_exempt
from .models import DishOrderTable, UserInputDishTable, Orders
import asyncio
import lebai_sdk as lebai_sdk
import nest_asyncio
import time

def generate_order_number(now):
    # 格式: YYMMDDHHmmss + 4位随机数 (例如: 2308101530451234)
    timestamp_part = now.strftime("%y%m%d%H%M%S")  # 12位时间字符串
    random_part = str(round(1000, 9999))  # 4位随机数

    return f"{timestamp_part}{random_part}"

@csrf_exempt  # <--- 在视图函数正上方添加这个装饰器
@require_POST
def submit_order(request):
    try:
        data = json.loads(request.body)
        cart_items = data.get('items', [])

        if not cart_items:
            return JsonResponse({'status': 'error', 'message': '购物车不能为空'}, status=400)
        """生成基于时间的订单号"""
        now = datetime.now()
        orders = Orders.objects.create(
            order_number = generate_order_number(now),
            status = 1,
            created_at = now,
            updated_at = now,
            payment_status = 1,
            paid_at = now
        )

        for item in cart_items:
            dish_id = item.get('id')
            if not dish_id:
                continue

            try:
                dish = DishOrderTable.objects.get(id=dish_id)

                UserInputDishTable.objects.create(
                    name="DefaultUser",  # 使用固定的默认用户名
                    order_id = orders.id,
                    dishname=dish.name,
                    price=dish.price,
                    calorie=dish.total_calorie,
                    carbon_emission=dish.total_carbon_emission,
                    protein=dish.total_protein,
                    fat=dish.total_fat,
                    carbohydrate=dish.total_carbohydrate
                )

            except DishOrderTable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': f'菜品ID {dish_id} 不存在'}, status=400)

        return JsonResponse({'status': 'success', 'order_id': orders.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



def init_mechanical_arm():
    lebai_sdk.init()
    nest_asyncio.apply()

    try:
        robot_ip = "192.168.101.147"
        print(f"尝试连接机器人 {robot_ip}...")

        lebai = lebai_sdk.connect(robot_ip, False)
        lebai.start_sys()  # 启动机器人
        # 获取当前状态
        state = lebai.get_robot_state()
        print(f"机器人当前状态: {state}")
        print('机器人急停原因：', lebai.get_estop_reason())

        # 获取当前运动数据
        kin_data = lebai.get_kin_data()
        print("机器人当前运动数据:")
        print(f"  关节角度: {kin_data['actual_joint_pose']}")
        print(f"  TCP 位姿: {kin_data['actual_tcp_pose']}")

        # 抓夹
        print("初始化夹爪...")
        try:
            lebai.init_claw()
            print("夹爪初始化成功")
        except Exception as e:
            print(f"夹爪初始化失败: {e}")
            return
        claw_status = lebai.get_claw()
        print("夹爪当前状态:")
        print(f"  力度: {claw_status['force']}")
        print(f"  开合度: {claw_status['amplitude']}")
        print(f"  是否夹住物体: {claw_status['hold_on']}")
        return lebai
    except Exception as e:
        print(f"发生错误：{e}")


#scene_id场景编号 需要调用的场景编号  lebai传入乐白初始化对象
def mechanical_arm_scene(scene_id,lebai):
    try:
        print("正在执行场景"+scene_id)
        while True:
            lebai.set_claw(force=1, amplitude=100)

            task_id = lebai.start_task(scene_id, None, None, False, 1)  # 调用场景 启动任务

            tasks = lebai.get_task_list()
            print('task_id ', task_id)
            print('tasks ', tasks)
            # 等待任务完成（可选）
            lebai.wait_task(task_id)
            print("等待执行场景" + scene_id)
            break

        # print("任务已完成，准备停止机器人...")

        # lebai.stop_sys()  # 停止手臂
        # lebai.estop()
        print("已完成场景" + scene_id)
    except Exception as e:
        print(f"主程序运行出错：{e}")

def stop_mechanical_arm_scene():

    if global_lebai is not None:
        global_lebai.estop()
        print("任务已完成，准备停止机器人...")
    else:
        print("机器人未启动")

global_lebai = None

@require_http_methods(["GET"])
def execute_task_one(request):
    global  global_lebai
    scene_id = request.GET.get('scene_id','')
    if scene_id != '':
        if global_lebai is None:
            global_lebai = init_mechanical_arm()
        mechanical_arm_scene(scene_id,global_lebai)
        return HttpResponse(f"成功")
    else:
        print("出现错误")
        return HttpResponse(f"出现错误")

def execute_task_two():
    lebai = init_mechanical_arm()
    mechanical_arm_scene("1012",lebai)