# main/api.py

import json
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt  # <--- 导入 csrf_exempt

from .models import Users, Dishes, OrderItems
from .models import Orders
from .models import ChatHistory
import lebai_sdk as lebai_sdk
import nest_asyncio


def generate_order_number(now):
    # 格式: YYMMDDHHmmss + 4位随机数 (例如: 2308101530451234)
    timestamp_part = now.strftime("%y%m%d%H%M%S")  # 12位时间字符串
    random_part = str(round(1000, 9999))  # 4位随机数

    return f"{timestamp_part}{random_part}"

@csrf_exempt  # <--- 在视图函数正上方添加这个装饰器
@require_POST
def submit_order(request):
    try:
        user = request.session.get("user")
        data = json.loads(request.body)
        cart_items = data.get('items', [])
        total_amount = 0
        if not cart_items:
            return JsonResponse({'status': 'error', 'message': '购物车不能为空'}, status=400)
        """生成基于时间的订单号"""
        now = timezone.now()
        orders = Orders.objects.create(
            status = "已出餐",
            order_time = now,
            total_amount = total_amount,
            user_id = user["user_id"]
        )

        for item in cart_items:
            dish_id = item.get('id')
            quantity = int(item.get('quantity'))
            if not dish_id:
                continue

            # try:
            dish = Dishes.objects.get(dish_id=dish_id)

            dish_price = dish.price*quantity
            OrderItems.objects.create(
                order_id = orders.order_id,
                dish_id=dish_id,
                quantity=quantity,
                dish_price=dish_price,
            )
            total_amount = total_amount + dish_price


            # except Dishes.DoesNotExist:
            #     return JsonResponse({'status': 'error', 'message': f'菜品ID {dish_id} 不存在'}, status=400)
        orders.total_amount = total_amount
        orders.save()
        return JsonResponse({'status': 'success', 'order_id': orders.order_id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def clear_chat_history(request):
    """清空聊天记录"""
    try:
        user = request.session.get("user")
        if not user:
            return JsonResponse({'status': 'error', 'message': '用户未登录'}, status=401)
            
        # 删除该用户的所有聊天记录
        deleted_count, _ = ChatHistory.objects.filter(
            user_id=user["user_id"]
        ).delete()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'已成功清空 {deleted_count} 条聊天记录'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



#登录api
def login_v(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            password = data.get('password')
            remember = data.get('remember', False)

            # 验证必填字段
            if not phone or not password:
                return JsonResponse({
                    'success': False,
                    'message': '手机号和密码不能为空',
                    'error_field': 'phone' if not phone else 'password'
                }, status=400)

            try:
                user = Users.objects.get(phone=phone)
            except Users.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在',
                    'error_field': 'phone'
                }, status=404)

            # 验证密码
            if not password == user.password:
                return JsonResponse({
                    'success': False,
                    'message': '密码错误',
                    'error_field': 'password'
                }, status=401)
            else:

                # 登录成功，返回用户基本信息
                user_data = {
                    'user_id': user.user_id,
                    'phone': user.phone,
                    'name': user.name,
                    'age': user.age,
                    'height': float(user.height) if user.height else None,
                    'weight': float(user.weight) if user.weight else None,
                    'gender': user.gender,
                    'allergens': user.allergens.split(',') if user.allergens else [],
                    'chronic_diseases': user.chronic_diseases.split(',') if user.chronic_diseases else []
                }
                # 存入session

                request.session['user'] = user_data
                # 在实际项目中，这里应该设置session或token
                response = JsonResponse({
                    'success': True,
                    'message': '登录成功',
                    'user': user_data
                })

                # 如果选择"记住我"，设置更长的session/cookie时间
                # if remember:
                #     request.session.set_expiry(30 * 24 * 60 * 60)  # 30天
                # else:
                #     request.session.set_expiry(0)  # 浏览器关闭时过期

            return response

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': '仅支持POST请求'
    }, status=405)


def logout (request):
    request.session.flush()
    return JsonResponse({
        'success': True,
        'message': '退出成功'
    })


def init_mechanical_arm():
    lebai_sdk.init()
    nest_asyncio.apply()

    try:
        robot_ip = "172.16.4.78"
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
def mechanical_arm_scene(scene_id):
    global  global_lebai
    try:
        print("正在执行场景"+scene_id)
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
#停止机械臂
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
from voice_service.dish_task_config import DISH_TASK_MAPPING, DISH_CATEGORIES, YOLO_CLASS_MAPPING

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


def detect_dish_with_yolo(dish_name, timeout=5, use_yolo=False):
    """使用YOLOv11检测菜品是否存在
    
    Args:
        dish_name: 菜品名称
        timeout: 检测超时时间（秒）
        use_yolo: 是否使用YOLO检测，False则直接返回True（跳过检测）- 默认False
    
    Returns:
        bool: 是否检测到菜品（或跳过检测时返回True）
    """
    # 如果不使用YOLO检测，直接返回True
    if not use_yolo:
        print(f'跳过YOLO检测，直接执行{dish_name}的任务')
        return True
    
    try:
        # 映射菜品名到YOLO类别
        target_class = YOLO_CLASS_MAPPING.get(dish_name)
        if not target_class:
            print(f'找不到{dish_name}的YOLO映射')
            return False

        # 实际调用YOLOv11检测接口
        import requests
        import time

        start_time = time.time()

        # 尝试连接到YOLO检测服务
        yolo_url = "http://172.16.4.223:5000/detect"
 
        while time.time() - start_time < timeout:
            try:
                # 调用YOLOv11检测API
                response = requests.get(yolo_url, params={'class': target_class}, timeout=1)

                if response.status_code == 200:
                    result = response.json()
                    if result.get('detected',False):
                        print(f'识别到{dish_name}')
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


def execute_dish_tasks(dish_list, order_id, use_yolo=False):
    """执行菜品任务流程
    
    Args:
        dish_list: 菜品列表
        order_id: 订单ID
        use_yolo: 是否使用YOLO检测，False则跳过检测直接执行任务 - 默认False
    """
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
        print(f"开始处理菜品: {dish}")

        # YOLO检测（可选）
        detected = detect_dish_with_yolo(dish, use_yolo=use_yolo)
        if not detected:
            if use_yolo:
                print(f"没有找到{dish}，请及时补货")
                continue
            else:
                print(f"跳过YOLO检测，直接执行{dish}的任务")

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
        detection_pose = [-2.7816824112321243, -1.653727163139964, -1.4043594113093043, -4.244045471083355, -1.390457710419091, 0.3760170406304678]

        a = 3  # 关节加速度 (rad/s2)
        v = 0.5  # 关节速度 (rad/s)
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
        a = 3  # 关节加速度 (rad/s2)
        v = 0.5  # 关节速度 (rad/s)
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
        vegetable_placement_pose = [-1.4868108786581578, -2.1268643624034413, -1.9606191945163352, -2.447658094670026, -1.2613157028389683, 0.0466905402312692]
        a = 3  # 关节加速度 (rad/s2)
        v = 0.5  # 关节速度 (rad/s)
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
        rice_detection_pose = [-0.24236896448593132, -2.0918704256798004, -0.7890413677686767, -4.941047991578893, -1.6037769137344378, -0.09328520666329557]

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
        a = 3  # 关节加速度 (rad/s2)
        v = 0.5  # 关节速度 (rad/s)
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
    """启动取餐流程
    
    参数:
        order_id: 订单ID（必需）
        use_yolo: 是否使用YOLO检测（可选，默认为false）
                  传入 'true', '1', 'yes' 表示使用YOLO
    """
    order_id = request.GET.get('order_id', '')
    use_yolo_param = request.GET.get('use_yolo', 'false').lower()
    
    # 解析use_yolo参数 - 只有明确指定true/1/yes时才使用YOLO
    use_yolo = use_yolo_param in ['true', '1', 'yes', 'on']

    if not order_id:
        return JsonResponse({'status': 'error', 'message': '订单ID不能为空'}, status=400)

    try:
        # 获取订单菜品 - 适配新的数据模型
        order_items = OrderItems.objects.filter(order_id=order_id).select_related('dish')
        dish_list = [item.dish.name for item in order_items]

        if not dish_list:
            return JsonResponse({'status': 'error', 'message': '订单中没有菜品'}, status=400)

        # 在新线程中执行取餐流程，避免阻塞请求
        pickup_thread = threading.Thread(
            target=execute_dish_tasks, 
            args=(dish_list, order_id, use_yolo)
        )
        pickup_thread.start()

        mode_msg = "使用YOLO检测" if use_yolo else "跳过YOLO检测"
        return JsonResponse({
            'status': 'success', 
            'message': f'取餐流程已开始执行（{mode_msg}）',
            'use_yolo': use_yolo
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def execute_order_tasks(request):
    """执行订单任务
    
    参数:
        order_id: 订单ID（必需）
        use_yolo: 是否使用YOLO检测（可选，默认为false）
                  传入 'true', '1', 'yes' 表示使用YOLO
    """
    order_id = request.GET.get('order_id', '')
    use_yolo_param = request.GET.get('use_yolo', 'false').lower()
    
    # 解析use_yolo参数 - 只有明确指定true/1/yes时才使用YOLO
    use_yolo = use_yolo_param in ['true', '1', 'yes', 'on']

    if not order_id:
        return JsonResponse({'status': 'error', 'message': '订单ID不能为空'}, status=400)

    try:
        # 获取订单菜品 - 适配新的数据模型
        order_items = OrderItems.objects.filter(order_id=order_id).select_related('dish')
        dish_list = [item.dish.name for item in order_items]

        if not dish_list:
            return JsonResponse({'status': 'error', 'message': '订单中没有菜品'}, status=400)

        # 在新线程中执行任务，避免阻塞请求
        task_thread = threading.Thread(
            target=execute_dish_tasks, 
            args=(dish_list, order_id, use_yolo)
        )
        task_thread.start()

        mode_msg = "使用YOLO检测" if use_yolo else "跳过YOLO检测"
        return JsonResponse({
            'status': 'success', 
            'message': f'任务已开始执行（{mode_msg}）',
            'use_yolo': use_yolo
        })

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


@csrf_exempt
@require_POST
def save_chat_message(request):
    """保存聊天记录"""
    try:
        user = request.session.get("user")
        if not user:
            return JsonResponse({'status': 'error', 'message': '用户未登录'}, status=401)
            
        data = json.loads(request.body)
        message = data.get('message', '')
        is_user = data.get('is_user', True)  # True表示用户消息，False表示AI回复
        
        if not message:
            return JsonResponse({'status': 'error', 'message': '消息内容不能为空'}, status=400)
            
        # 创建聊天记录
        chat_history = ChatHistory.objects.create(
            user_id=user["user_id"],
            message=message,
            is_user=is_user,
            timestamp=timezone.now()
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': '聊天记录保存成功',
            'chat_id': chat_history.chat_id
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def get_chat_history(request):
    """获取聊天记录"""
    try:
        user = request.session.get("user")
        if not user:
            return JsonResponse({'status': 'error', 'message': '用户未登录'}, status=401)
            
        # 获取参数
        limit = int(request.GET.get('limit', 20))  # 默认获取最近20条记录
        offset = int(request.GET.get('offset', 0))  # 偏移量，用于分页
        
        # 查询用户的聊天记录，按时间倒序排列
        chat_history = ChatHistory.objects.filter(
            user_id=user["user_id"]
        ).order_by('-timestamp')[offset:offset+limit]
        
        # 格式化返回数据
        history_data = []
        for chat in chat_history:
            history_data.append({
                'chat_id': chat.chat_id,
                'message': chat.message,
                'is_user': chat.is_user,
                'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'status': 'success', 
            'chat_history': history_data
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
