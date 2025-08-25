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
            order_number=generate_order_number(now),
            status=1,
            created_at=now,
            updated_at=now,
            payment_status=1,
            paid_at=now
        )

        for item in cart_items:
            dish_id = item.get('id')
            if not dish_id:
                continue

            try:
                dish = DishOrderTable.objects.get(id=dish_id)

                UserInputDishTable.objects.create(
                    name="DefaultUser",  # 使用固定的默认用户名
                    order_id=orders.id,
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


# scene_id场景编号 需要调用的场景编号  lebai传入乐白初始化对象
def mechanical_arm_scene(scene_id):
    global global_lebai
    try:
        print("正在执行场景" + scene_id)
        while True:
            global_lebai.set_claw(force=1, amplitude=100)

            task_id = global_lebai.start_task(scene_id, None, None, False, 1)  # 调用场景 启动任务

            tasks = global_lebai.get_task_list()
            print('task_id ', task_id)
            print('tasks ', tasks)
            # 等待任务完成（可选）
            global_lebai.wait_task(task_id)
            print("等待执行场景" + scene_id)
            break

        # print("任务已完成，准备停止机器人...")

        # lebai.stop_sys()  # 停止手臂
        # lebai.estop()
        print("已完成场景" + scene_id)
    except Exception as e:
        print(f"主程序运行出错：{e}")


# 停止机械臂
def stop_mechanical_arm_scene():
    if global_lebai is not None:
        global_lebai.estop()
        print("任务已完成，准备停止机器人...")
    else:
        print("机器人未启动")


global_lebai = None

# 导入配置文件
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dish_task_config import DISH_TASK_MAPPING, DISH_CATEGORIES, YOLO_CLASS_MAPPING, ROBOT_CONFIG

import requests
import threading
import time


def classify_and_sort_dishes(dish_list):
    """按分类排序菜品：肉类->素菜->主食"""
    sorted_dishes = []

    # 按顺序添加各类菜品
    for category in ['肉类', '素菜', '主食']:
        for dish in dish_list:
            if dish in DISH_CATEGORIES[category] and dish in DISH_TASK_MAPPING:
                sorted_dishes.append(dish)

    return sorted_dishes


def detect_dish_with_yolo(dish_name, timeout=5):
    """使用YOLOv11检测菜品是否存在"""
    try:
        # 映射菜品名到YOLO类别
        target_class = YOLO_CLASS_MAPPING.get(dish_name)
        if not target_class:
            print(f"未找到{dish_name}对应的YOLO类别")
            return False

        # 实际调用YOLOv11检测接口
        import requests
        import time

        start_time = time.time()

        # 尝试连接到YOLO检测服务
        yolo_url = "http://localhost:5000/detect"
 
        while time.time() - start_time < timeout:
            try:
                # 调用YOLOv11检测API
                response = requests.get(yolo_url, params={'class': target_class}, timeout=1)

                if response.status_code == 200:
                    result = response.json()
                    if result.get('detected', False):
                        print(f"检测到{dish_name}")
                        return True

                # 等待0.5秒后重试
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"连接YOLO服务失败: {e}")
                time.sleep(0.5)

        # 超时未检测到
        print(f"没有找到{dish_name}，请及时补货")
        return False

    except Exception as e:
        print(f"检测{dish_name}时出错: {e}")
        return False


def execute_dish_tasks(dish_list, order_id):
    """执行菜品任务流程"""
    global global_lebai

    # 分类排序菜品
    sorted_dishes = classify_and_sort_dishes(dish_list)
    print(f"排序后的菜品列表: {sorted_dishes}")

    # 初始化机械臂
    if global_lebai is None:
        global_lebai = init_mechanical_arm()

    # 移动到菜品识别区域
    move_to_detection_area()

    # 逐个检测并执行任务
    for dish in sorted_dishes:
        print(f"开始检测菜品: {dish}")

        # YOLO检测
        detected = detect_dish_with_yolo(dish)
        if not detected:
            print(f"没有找到{dish}，请及时补货")
            continue

        # 获取任务ID
        task_id = DISH_TASK_MAPPING.get(dish)
        if not task_id:
            print(f"未找到{dish}对应的任务ID")
            continue

        print(f"执行{dish}的任务ID: {task_id}")
        mechanical_arm_scene(task_id)

        # 根据菜品分类执行后续操作
        dish_category = get_dish_category(dish)
        if dish_category == '肉类':
            execute_meat_dish_placement()
        elif dish_category == '素菜':
            execute_vegetable_dish_placement()
        elif dish_category == '主食':
            execute_staple_dish_placement()

    print(f"订单{order_id}的所有任务执行完成")


def get_dish_category(dish_name):
    """获取菜品分类"""
    for category, dishes in DISH_CATEGORIES.items():
        if dish_name in dishes:
            return category
    return None


def move_to_detection_area():
    """移动机械臂到菜品识别区域"""
    global global_lebai
    try:
        # 菜品识别区域的目标位姿关节数据参数
        detection_pose = [-2.995385109744443, -2.451109551442769, -0.31302795452791365, -1.5946689028063668,
                          1.3373436256385505, 0.3972051502631382]  # 需要填写实际坐标
        a = 5  # 关节加速度 (rad/s2)
        v = 1  # 关节速度 (rad/s)
        t = 0  # 运动时间 (s)
        r = 0.5  # 交融半径 (m)

        print("移动到菜品识别区域...")
        motion_id = global_lebai.movej(detection_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到菜品识别区域失败，运动状态: {move_state}")

        print("已到达菜品识别区域")
    except Exception as e:
        print(f"移动到识别区域失败: {e}")
        raise  # 重新抛出异常以便上层处理


def execute_meat_dish_placement():
    """执行肉类菜品放置操作"""
    global global_lebai
    try:
        # 肉类菜品放置位置的目标位姿关节数据参数
        meat_placement_pose = [-1.082798688648777, -2.1748012620248676, -1.989956577084648, -2.281125305385191,
                               -0.9109928404055851, 0.13997574689456477]
        a = 5  # 关节加速度 (rad/s2) - int类型
        v = 1  # 关节速度 (rad/s) - int类型（修复：从1.5改为1）
        t = 0  # 运动时间 (s)
        r = 0.5  # 交融半径 (m)

        print("移动到肉类菜品放置位置...")
        motion_id = global_lebai.movej(meat_placement_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到肉类放置位置失败，运动状态: {move_state}")

        # 打开抓夹
        print("打开抓夹...")
        global_lebai.set_claw(force=100, amplitude=100)  # 使用set_claw方法，force对应力度，amplitude对应开合度
        time.sleep(0.5)

        # 验证抓夹是否打开
        claw_status = global_lebai.get_claw()
        is_open = claw_status['amplitude'] >= 90  # 开合度大于90认为已打开
        if not is_open:
            print("警告：抓夹可能未完全打开，尝试重新打开...")
            global_lebai.set_claw(force=0, amplitude=100)
            time.sleep(1)

        # 调整至肉菜目标位姿
        meat_target_pose = [-0.9808848400536246, -2.138273344513341, -2.044029399857617, -2.3127636591353324,
                            -0.7584576258102067, 0.1868580347243197]  # 需要填写实际坐标
        motion_id = global_lebai.movej(meat_target_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"调整至肉菜目标位姿失败，运动状态: {move_state}")

        # 移动至安全位置
        safer_pose = [-1.3016785723202091, -1.1531700572930308, -2.0116240557135328, -3.141688527389036,
                      -1.106191895664033, 0.025885925795570194]
        motion_id = global_lebai.movej(safer_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到更安全位置失败，运动状态: {move_state}")

        # 返回菜品识别区域
        move_to_detection_area()
        print("肉类菜品放置完成")

    except Exception as e:
        print(f"肉类菜品放置失败: {e}")
        raise  # 重新抛出异常以便上层处理


def execute_vegetable_dish_placement():
    """执行素菜菜品放置操作"""
    global global_lebai
    try:
        # 素菜菜品放置位置
        vegetable_placement_pose = [-1.5985997285753235, -2.136259994729241, -2.0316616797552887, -2.293684773086005,
                                    -1.3938132933925906, 0.01265534150005654]  # 需要填写实际坐标
        a = 5  # 关节加速度 (rad/s2) - int类型
        v = 1  # 关节速度 (rad/s) - int类型（修复：从1.5改为1）
        t = 0  # 运动时间 (s)
        r = 0.5  # 交融半径 (m)

        print("移动到素菜菜品放置位置...")
        motion_id = global_lebai.movej(vegetable_placement_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到素菜放置位置失败，运动状态: {move_state}")

        # 打开抓夹
        print("打开抓夹...")
        global_lebai.set_claw(force=30, amplitude=100)  # 使用set_claw方法，force对应力度，amplitude对应开合度
        time.sleep(0.5)

        # 验证抓夹是否打开
        claw_status = global_lebai.get_claw()
        is_open = claw_status['amplitude'] >= 90  # 开合度大于90认为已打开
        if not is_open:
            print("警告：抓夹可能未完全打开，尝试重新打开...")
            global_lebai.set_claw(force=30, amplitude=100)
            time.sleep(1)

        # 移动至素菜安全离开抓夹位置
        vegetable_safe_leave_pose = [-1.558907975688783, -2.0871726095169003, -2.3258983696316036, -1.9253376363949657,
                                     -1.344821781979493, 0.01524393407961356]  # 需要填写实际坐标
        motion_id = global_lebai.movej(vegetable_safe_leave_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到素菜安全离开位置失败，运动状态: {move_state}")

        # 移动至安全位置
        safer_pose = [-1.3016785723202091, -1.1531700572930308, -2.0116240557135328, -3.141688527389036,
                      -1.106191895664033, 0.025885925795570194]
        motion_id = global_lebai.movej(safer_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到更安全位置失败，运动状态: {move_state}")

        # 移动至米饭识别区域
        rice_detection_pose = [-0.2552160535844735, -2.03405852473636, -1.4311082012980605, -4.424767582656132,
                               -1.5800960853214532, 0.038637141094869584]  # 需要填写实际坐标
        motion_id = global_lebai.movej(rice_detection_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到米饭识别区域失败，运动状态: {move_state}")

        print("素菜菜品放置完成")

    except Exception as e:
        print(f"素菜菜品放置失败: {e}")
        raise  # 重新抛出异常以便上层处理


def execute_staple_dish_placement():
    """执行主食菜品放置操作"""
    global global_lebai
    try:
        # 主食菜品放置位置的笛卡尔坐标参数（使用实际坐标而非零坐标）
        staple_placement_pose = [-1.0432986833607216, -1.9819031779482483, -2.423881392457799, -2.12849421699057,
                                 -0.8266238970718749, 0.1564660403643354]  # 需要填写实际坐标
        a = 5  # 关节加速度 (rad/s2) - int类型
        v = 1  # 关节速度 (rad/s) - int类型（修复：从1.5改为1）
        t = 0  # 运动时间 (s)
        r = 0.5  # 交融半径 (m)

        print("移动到主食菜品放置位置...")
        motion_id = global_lebai.movej(staple_placement_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到主食放置位置失败，运动状态: {move_state}")

        # 打开抓夹
        print("打开抓夹...")
        global_lebai.set_claw(force=30, amplitude=100)  # 使用set_claw方法，force对应力度，amplitude对应开合度
        time.sleep(0.5)

        # 验证抓夹是否打开
        claw_status = global_lebai.get_claw()
        is_open = claw_status['amplitude'] >= 90  # 开合度大于90认为已打开
        if not is_open:
            print("警告：抓夹可能未完全打开，尝试重新打开...")
            global_lebai.set_claw(force=30, amplitude=100)
            time.sleep(1)

        # 移动至主食安全离开抓夹位置
        staple_safe_leave_pose = [-0.7658399083519064, -1.9051082647547235, -2.60575398962149, -2.0790233365812583,
                                  -0.5393859945402886, 0.29529130166798595]  # 需要填写实际坐标
        motion_id = global_lebai.movej(staple_safe_leave_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到主食安全离开位置失败，运动状态: {move_state}")

            # 移动至安全位置
        safer_pose = [-1.3016785723202091, -1.1531700572930308, -2.0116240557135328, -3.141688527389036,
                      -1.106191895664033, 0.025885925795570194]
        motion_id = global_lebai.movej(safer_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"移动到更安全位置失败，运动状态: {move_state}")

        # 返回初始位置
        initial_pose = [-1.8648412690727256, -1.7554492641366306, -2.64103554774286, -1.89187768045921,
                        0.022530342822070355, 0.11466506389445168]  # 需要填写实际坐标
        motion_id = global_lebai.movej(initial_pose, a, v, t, r)
        global_lebai.wait_move(motion_id)

        # 验证运动是否完成
        move_state = global_lebai.get_motion_state(motion_id)
        if move_state != "FINISHED":
            raise Exception(f"返回初始位置失败，运动状态: {move_state}")

        print("主食菜品放置完成")

    except Exception as e:
        print(f"主食菜品放置失败: {e}")
        raise  # 重新抛出异常以便上层处理


@require_http_methods(["GET"])
def start_pickup_process(request):
    """启动取餐流程"""
    order_id = request.GET.get('order_id', '')

    if not order_id:
        return JsonResponse({'status': 'error', 'message': '订单ID不能为空'}, status=400)

    try:
        # 获取订单菜品
        order_dishes = UserInputDishTable.objects.filter(order_id=order_id)
        dish_list = [dish.dishname for dish in order_dishes]

        if not dish_list:
            return JsonResponse({'status': 'error', 'message': '订单中没有菜品'}, status=400)

        # 在新线程中执行取餐流程，避免阻塞请求
        pickup_thread = threading.Thread(target=execute_dish_tasks, args=(dish_list, order_id))
        pickup_thread.start()

        return JsonResponse({'status': 'success', 'message': '取餐流程已开始执行'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def execute_order_tasks(request):
    """执行订单任务"""
    order_id = request.GET.get('order_id', '')

    if not order_id:
        return JsonResponse({'status': 'error', 'message': '订单ID不能为空'}, status=400)

    try:
        # 获取订单菜品
        order_dishes = UserInputDishTable.objects.filter(order_id=order_id)
        dish_list = [dish.dishname for dish in order_dishes]

        if not dish_list:
            return JsonResponse({'status': 'error', 'message': '订单中没有菜品'}, status=400)

        # 在新线程中执行任务，避免阻塞请求
        task_thread = threading.Thread(target=execute_dish_tasks, args=(dish_list, order_id))
        task_thread.start()

        return JsonResponse({'status': 'success', 'message': '任务已开始执行'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def execute_task_one(request):
    global global_lebai
    scene_id = request.GET.get('scene_id', '')
    if scene_id != '':
        if global_lebai is None:
            global_lebai = init_mechanical_arm()
        mechanical_arm_scene(scene_id)
        return HttpResponse(f"成功")
    else:
        print("出现错误")
        return HttpResponse(f"出现错误")


def execute_task_two():
    lebai = init_mechanical_arm()
    mechanical_arm_scene("1012", lebai)