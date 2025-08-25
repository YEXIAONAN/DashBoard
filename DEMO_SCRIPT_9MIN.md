# 智慧食堂机器人系统 9分钟演示逐字稿

## 开场 1分钟 - 项目整体介绍

【讲解】欢迎来到智慧食堂机器人系统演示。这是一个完整的"点餐-视觉识别-机械臂执行"闭环系统。用户手机点餐→YOLOv5视觉识别菜品→机械臂精准抓取→完成配餐。今天我们将深入技术细节，看如何用代码实现这个智能流程。

## 核心模块1：视觉识别 2.5分钟

【讲解】先看视觉识别模块，这是整个系统的眼睛。我们使用YOLOv5模型，需要解决两个核心问题：如何实时检测菜品，以及如何处理检测超时。

【代码】```python
# yolov5_stream.py - 核心检测类
class YOLODetector:
    def __init__(self):
        self.device = select_device('0' if torch.cuda.is_available() else 'cpu')
        self.detected_classes = []  # 实时存储检测到的菜品
        self.lock = threading.Lock()  # 线程安全
```

【讲解】这里的关键是线程安全的检测结果存储，避免机械臂读取时出现竞态条件。

【代码】```python
# 5秒超时检测逻辑
def detect_dish_with_yolo(dish_name, timeout=5):
    target_class = YOLO_CLASS_MAPPING.get(dish_name)  # 菜品名映射到YOLO类别
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get('http://localhost:5000/detect', 
                              params={'class': target_class}, timeout=1)
        if response.json().get('detected', False):
            return True  # 检测到菜品，触发机械臂动作
        time.sleep(0.5)  # 降低CPU占用
    
    print(f"未检测到{dish_name}，请及时补货")  # 超时处理
    return False
```

【讲解】5秒超时设计是为了及时提醒补货，避免机械臂空转浪费资源。每次检测间隔0.5秒，既保证实时性又控制API调用频率。

## 核心模块2：机械臂控制 2.5分钟

【讲解】视觉识别后，需要将检测结果转化为机械臂动作。这里用到乐白机械臂SDK，关键是如何将菜品映射到具体的机械臂场景。

【代码】```python
# api.py - 机械臂控制核心
class TaskConfig:
    # 菜品到机械臂场景的映射
    DISH_TASK_MAPPING = {
        '红烧排骨': '1001',  # 肉类场景
        '清炒莲藕': '1002',  # 素菜场景
        '米饭': '1003'       # 主食场景
    }

def init_mechanical_arm():
    lebai = lebai_sdk.connect("192.168.101.147", False)  # 连接机械臂
    lebai.start_sys()  # 启动系统
    lebai.init_claw()  # 初始化夹爪
    return lebai
```

【讲解】每个菜品对应独立的场景ID，这是为了处理不同菜品的抓取策略差异。肉类需要更大力度，素菜需要更轻柔。

【代码】```python
# 机械臂动作执行
def mechanical_arm_scene(scene_id):
    global global_lebai
    
    # 设置夹爪力度和开合度
    global_lebai.set_claw(force=1, amplitude=100)
    
    # 启动对应场景任务
    task_id = global_lebai.start_task(scene_id, None, None, False, 1)
    global_lebai.wait_task(task_id)  # 同步等待完成
```

【讲解】force=1是最小力度，适合大多数菜品。amplitude=100是最大开合度，确保能抓取不同大小的餐盘。

## 核心模块3：协同逻辑 2分钟

【讲解】现在看视觉和机械臂如何协同工作。关键在execute_dish_tasks函数，它实现了完整的"检测-执行"闭环。

【代码】```python
def execute_dish_tasks(dish_list, order_id):
    # 1. 菜品分类排序：肉类→素菜→主食
    sorted_dishes = classify_and_sort_dishes(dish_list)
    
    # 2. 逐个检测并执行
    for dish in sorted_dishes:
        print(f"开始检测: {dish}")
        
        # 视觉检测
        if detect_dish_with_yolo(dish):  # 5秒超时检测
            task_id = DISH_TASK_MAPPING[dish]  # 获取对应场景
            mechanical_arm_scene(task_id)      # 执行机械臂动作
        else:
            continue  # 未检测到，跳过此菜品
```

【讲解】分类排序是为了避免机械臂频繁切换工具，提高效率。肉类先处理，因为通常需要更长时间。

【代码】```python
# 前端触发接口 - 非阻塞设计
@require_http_methods(["GET"])
def execute_order_tasks(request):
    order_id = request.GET.get('order_id', '')
    
    # 获取订单菜品
    order_dishes = UserInputDishTable.objects.filter(order_id=order_id)
    dish_list = [dish.dishname for dish in order_dishes]
    
    # 新线程执行，避免阻塞HTTP请求
    task_thread = threading.Thread(target=execute_dish_tasks, args=(dish_list, order_id))
    task_thread.start()
    
    return JsonResponse({'status': 'success', 'message': '任务已开始执行'})
```

【讲解】使用线程异步执行是关键，避免用户等待机械臂完成。前端点击"取餐"后立即返回，后台继续执行任务。

## 前端交互：实时状态反馈 1分钟

【讲解】最后看前端如何给用户实时反馈。order_status.html实现了"点击取餐→显示机械臂动画→完成提示"的完整交互。

【代码】```javascript
// order_status.html - 取餐按钮逻辑
function qucan() {
    fetch(`/execute_order_tasks/?order_id=${orderId}`)
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                showModal();  // 显示机械臂动画弹窗
                // 2秒后自动关闭并刷新页面
                setTimeout(() => {
                    closeModal();
                    location.reload();
                }, 2000);
            }
        });
}
```

【讲解】2秒动画展示是为了给用户心理预期，实际机械臂可能需要更长时间，但前端不需要等待。

## 结尾 1分钟 - 技术亮点总结

【讲解】总结一下技术亮点：
1. **视觉精准**：YOLOv5模型实现5秒内菜品识别，支持中文菜品名映射
2. **协同高效**：线程异步执行+菜品分类排序，避免机械臂空转
3. **用户体验**：前端非阻塞设计+动画反馈，用户无需等待
4. **异常处理**：超时检测+补货提醒，系统鲁棒性强

整个系统实现了真正的"点餐-识别-执行"闭环，用代码让机器人真正"看懂"并"拿到"菜品。这就是智慧食堂的核心技术。