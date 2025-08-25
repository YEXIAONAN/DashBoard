# 乐白机器人Python SDK运动控制接口教程  
本文档详细介绍乐白机器人Python SDK中与运动控制相关的接口使用方法，包括示教模式切换、关节运动、直线运动、圆弧运动等核心功能，帮助开发者快速掌握机器人运动控制逻辑。


初始化连接
设备发现
注意

本功能基于 mDNS 技术，用于 Web 前端开发的 JavaScript SDK 不支持该功能

devices = lebai_sdk.discover_devices(time)
在持续时间内连续发现周边设备，持续时间结束后，返回发现的设备的名称、IP、MAC 地址。

参数

time 持续时间

列表类型。列表里包含搜到的设备结果，每个设备对象的属性(设备的名称、IP、MAC 地址)以字典形式呈现
name 设备的名称
ip 设备IP
mac 设备MAC 地址
示例程序
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()

devices = lebai_sdk.discover_devices(3)
print(devices)
# 输出：
# [{'name': 'lebai-3wbgvM', 'mac': 'b4:4b:d6:5e:55:1c', 'ip': '10.20.17.1', 'online': True}]
初始化对象
注意

由于通信不稳定,ip错误等原因，可能导致错误发生。大多数情况下，需要使用错误处理机制来捕获错误，防止异常退出。

lebai = lebai_sdk.connect(ip, simu)
连接到乐白机械臂

参数

ip 乐白机械臂的 IP 地址
simu 是否以仿真模式连接。可选，默认真机模式

lebai 机械臂实例，后续控制机械臂的方法需使用该实例
示例程序
import lebai_sdk
lebai_sdk.init()

# 如果出现event loop相关的RuntimeError，尝试添加以下2行
# import nest_asyncio
# nest_asyncio.apply()

# 设定机器人ip地址，需要根据机器人实际ip地址修改
robot_ip = "192.168.4.145" 
# 创建实例  
lebai = lebai_sdk.connect(robot_ip, False) 
获取连接状态
connected = lebai.is_connected()
返回连接状态。用于判断是否处于连接状态，如果重启手臂会断连。
connected 连接状态
示例程序
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.123" 
try:
    lebai = lebai_sdk.connect(robot_ip, False) 
    connected = lebai.is_connected()
    if not connected:
        print('机器断连')
        disconnect_reason = lebai.wait_disconnect()
        print(disconnect_reason)

except Exception as e:
    print('初始化对象失败： %s'%e)
等待断开连接
disconnect_reason = lebai.wait_disconnect()
返回连接断开后的断开原因。如果检测到手臂断开连接，判断断开原因，重新连接。

disconnect_reason 断开连接的原因
示例程序
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.123" 
try:
    lebai = lebai_sdk.connect(robot_ip, False) 
    connected = lebai.is_connected()
    if not connected:
        print('机器断连')
        disconnect_reason = lebai.wait_disconnect()
        print(disconnect_reason)
        lebai = lebai_sdk.connect(robot_ip, False) 

except Exception as e:
    print('初始化对象失败： %s'%e)



# Lebai Python SDK 爪子控制教程

## 一、爪子控制简介
爪子（夹持器）是机器人的重要执行部件，Lebai Python SDK 提供了丰富的接口用于控制爪子的开合、设置力度等操作。本教程将详细介绍同步和异步方式下的爪子控制方法。

## 二、同步方式控制爪子

### 2.1 基本爪子控制示例
```python
# 导入同步客户端类
from lebai_sdk import LebaiClient

# 初始化客户端，连接到机器人
# 替换为实际机器人IP
client = LebaiClient("192.168.1.100")
client.connect()

try:
    # 打开爪子
    # 该方法会控制爪子执行打开动作
    client.open_gripper()
    
    # 等待爪子动作完成（可选，根据实际情况调整等待时间）
    import time
    time.sleep(2)  # 等待2秒
    
    # 关闭爪子
    # 控制爪子执行关闭动作
    client.close_gripper()
    
    # 等待爪子关闭完成
    time.sleep(2)

finally:
    # 断开连接，释放资源
    client.disconnect()
```

### 2.2 带参数的爪子控制
```python
from lebai_sdk import LebaiClient
import time

client = LebaiClient("192.168.1.100")
client.connect()

try:
    # 自定义参数打开爪子
    # speed: 爪子开合度（0-100）
    # force: 爪子作用力（0-100）
    client.open_gripper(speed=50, force=30)
    time.sleep(2)
    
    # 自定义参数关闭爪子
    # 关闭时可以设置更大的力度
    client.close_gripper(speed=0, force=80)
    time.sleep(2)

finally:
    client.disconnect()
```

### 2.3 设置爪子参数
```python
from lebai_sdk import LebaiClient

client = LebaiClient("192.168.1.100")
client.connect()

try:
    # 设置爪子最大开度（单位：米）
    # 根据实际爪子型号调整该参数
    client.set_gripper_max_width(0.1)  # 设置为0.1米
    
    # 设置爪子最小开度（单位：米）
    client.set_gripper_min_width(0)
    
    # 获取当前爪子开度
    current_width = client.get_gripper_width()
    print(f"当前爪子开度: {current_width} 米")

finally:
    client.disconnect()
```

## 三、异步方式控制爪子

### 3.1 基本异步爪子控制
```python
# 导入异步客户端和asyncio库
from lebai_sdk_asyncio import AsyncLebaiClient
import asyncio

# 定义异步函数
async def control_gripper():
    # 创建异步客户端并连接机器人
    async with AsyncLebaiClient("192.168.1.100") as client:
        await client.connect()
        
        # 异步打开爪子
        await client.open_gripper()
        # 等待动作完成
        await asyncio.sleep(2)
        
        # 异步关闭爪子
        await client.close_gripper()
        await asyncio.sleep(2)

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(control_gripper())
```

### 3.2 异步方式设置爪子参数
```python
from lebai_sdk_asyncio import AsyncLebaiClient
import asyncio

async def set_gripper_params():
    async with AsyncLebaiClient("192.168.1.100") as client:
        await client.connect()
        
        # 异步设置爪子参数
        await client.set_gripper_max_width(0.12)
        await client.set_gripper_min_width(0.01)
        
        # 异步获取爪子状态
        width = await client.get_gripper_width()
        is_open = await client.is_gripper_open()
        is_closed = await client.is_gripper_closed()
        
        print(f"当前开度: {width}米")
        print(f"是否完全打开: {is_open}")
        print(f"是否完全关闭: {is_closed}")

if __name__ == "__main__":
    asyncio.run(set_gripper_params())
```

## 四、爪子控制常用API参数说明

| 方法 | 参数 | 说明 |
|------|------|------|
| open_gripper() | speed: 速度(0-100)<br>force: 力度(0-100) | 打开爪子 |
| close_gripper() | speed: 速度(0-100)<br>force: 力度(0-100) | 关闭爪子 |
| set_gripper_max_width() | width: 最大宽度(米) | 设置爪子最大开度 |
| set_gripper_min_width() | width: 最小宽度(米) | 设置爪子最小开度 |
| get_gripper_width() | 无 | 获取当前爪子开度(米) |
| is_gripper_open() | 无 | 判断爪子是否完全打开 |
| is_gripper_closed() | 无 | 判断爪子是否完全关闭 |

## 五、爪子控制注意事项
1. 控制爪子前确保机器人已正确连接，且爪子处于正常工作状态
2. 首次使用时应先校准爪子的最大和最小开度，确保与实际机械结构匹配
3. 力度参数设置应适当，过大可能损坏爪子或抓取对象，过小可能导致抓取不稳
4. 执行爪子动作后，建议添加适当的等待时间，确保动作完成后再执行后续操作
5. 抓取易碎物品时，应降低力度参数，避免损坏物品
6. 若爪子无反应，检查是否有机械故障或参数设置是否在合理范围内



运动
示教模式
lebai.teach_mode()
当机器人处于空闲状态时，调用该指令可进入示教（自由驱动）模式。
在示教模式下，机器人各关节可被自由拖拽，故又称自由驱动模式。
末端负载配置会影响示教效果，设置值比实际负载大时，机器人会向上用力，反之则会向下用力，请注意检查。
返回值：无返回值。
注意

注意：当机器人处于非空闲状态时，调用该指令将会产生错误 1000: 机器人处于空闲中才能示教。

使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
lebai.teach_mode()
退出示教模式
lebai.end_teach_mode()
当机器人处于示教中状态，即示教（自由驱动）模式时，调用该指令可退出示教模式，恢复到空闲状态。处与其他模式时调用不产生错误。
返回值：无返回值。
使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
lebai.end_teach_mode()

## 关节运动
motion_id = lebai.movej(p, a, v, t, r)
在关节空间内执行线性运动。使用该命令，机器人必须处于静止状态或者上一个命令是 movej 或者带交融的 movel。

参数	类型	说明
p	list/dict	位置参数。 若是 [0.1, 0.2, 0.2, 0.3, 0.1, 0.2]，表示关节角表达的关节位置
若是 {'x': 0.01, 'y': 0, 'z': 0, 'rz': 0, 'ry':0, 'rx':0}，则表示的是笛卡尔坐标位置
a	int	运动的关节加速度 (rad/s2)
v	int	运动的关节速度 (rad/s)
t	int	运动时间 (s)。 当 t > 0 时，参数速度v和加速度a无效。
如果时间很短，可能在设定时间内，完不成运动指令，但会以安全设置的最大加速度和速度移动到目标置。
r	int	运动轨迹交融半径 (m)。用于指定路径的平滑效果，范围0到1。
数值越大，连续走多点运动时，允许偏离轨迹路径的值越大，轨迹弧度越大以达到平滑效果
注意：

当位置参数是笛卡尔坐标位置时，如果输入的笛卡尔坐标位置是奇异点或者超出运动范围，反解不出来，就会报错。
安全设置里有各个关节的安全角度范围设置，如果输入的关节位置，某个关节角度超出范围，运动过程中会报错，须根据需求设置关节安全角度范围。
返回值：int类型。返回运动指令id。

使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False)

joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id1 = lebai.movej(joint_pose,a,v,t,r)  
motion_id2 = lebai.movej(cartesian_pose,a,v,t,r) 


## 关节跟随运动
motion_id = lebai.towardj(p, a, v, t, r)
参数介绍

参数	类型	说明
p	list/dict	位置参数。 若是 [0.1, 0.2, 0.2, 0.3, 0.1, 0.2]，表示关节角表达的关节位置
若是 {'x': 0.01, 'y': 0, 'z': 0, 'rz': 0, 'ry':0, 'rx':0}，则表示的是笛卡尔坐标位置
a	int	运动的关节加速度 (rad/s2)
v	int	运动的关节速度 (rad/s)
t	int	运动时间 (s)。 当 t > 0 时，参数速度v和加速度a无效。
如果时间很短，可能在设定时间内，完不成运动指令，但会以安全设置的最大加速度和速度移动到目标置。
r	int	运动轨迹交融半径 (m)。用于指定路径的平滑效果，范围0到1。
数值越大，连续走多点运动时，允许偏离轨迹路径的值越大，轨迹弧度越大以达到平滑效果
连续发出towardj运动指令，会忽略前面发出的运动目标位置，不需要运动到之前发出的目标位置，会以最新指令的位置参数为目标，进行运动。 注意：与movej不同，movej指令发出位置，形成轨迹，手臂会按照轨迹一步步执行完成。

返回值：int类型。返回运动指令id。

使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
 
joint_pose1 = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
joint_pose2 = [0.3,-1.05,1.05,0,1.57,0] 
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id1 = lebai.towardj(joint_pose1,a,v,t,r)
motion_id2 = lebai.towardj(joint_pose2,a,v,t,r) #会直接移动到joint_pose2，忽略joint_pose1位置
关节匀速运动
motion_id = lebai.speedj(a, v, t)
参数介绍

参数	类型	说明
a	int	运动的关节加速度 (rad/s2)
v	list	运动的关节速度 (rad/s) 。如[0.1, 0.2, 0.2, 0.3, 0.1, 0.2]
t	int	运动时间 (s)。可空，默认t = 0，一直运动到限位
不指定位置，各个关节按照速度矢量定速运动，运动多久根据运动时间参数而定，默认t = 0，一直运动到限位。
收到其他运动指令后，会立即终止当前指令，并执行新运动指令。

注意：速度参数是列表，代表各个关节的速度设定值。不同于movej的整数类型。

返回值：int类型。返回运动指令id。

使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
a = 5 #关节加速度 (rad/s2)
v =[0.1, 0.2, 0.2, 0.3, 0.1, 0.2]
t = 0.2   
motion_id = lebai.speedj(a,v,t)
直线运动
motion_id = lebai.movel(p, a, v, t, r)
参数介绍

参数	类型	说明
p	list/dict	位置参数。 若是 [0.1, 0.2, 0.2, 0.3, 0.1, 0.2]，表示关节角表达的关节位置
若是 {'x': 0.01, 'y': 0, 'z': 0, 'rz': 0, 'ry':0, 'rx':0}，则表示的是笛卡尔坐标位置
a	int	运动的工具空间加速度 (m/s2)
v	int	运动的工具空间速度(m/s)
t	int	运动时间 (s)。 当 t > 0 时，参数速度v和加速度a无效。
如果时间很短，可能在设定时间内，完不成运动指令，但会以安全设置的最大加速度和速度移动到目标置。
r	int	运动轨迹交融半径 (m)。用于指定路径的平滑效果，范围0到1。
数值越大，连续走多点运动时，允许偏离轨迹路径的值越大，轨迹弧度越大以达到平滑效果
返回值：int类型。返回运动指令id。

注意

当位置参数是笛卡尔坐标位置时，如果输入的笛卡尔坐标位置是奇异点或者超出运动范围，反解不出来，就会报错。
安全设置里有各个关节的安全角度范围设置，如果输入的关节位置，某个关节角度超出范围，运动过程中会报错，须根据需求设置关节安全角度范围。
使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
 
joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据

a = 2 #空间加速度 (m/s2)
v = 1 #空间速度 （m/s）
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5  #交融半径 (m)。用于指定路径的平滑效果
motion_id1 = lebai.movel(joint_pose,a,v,t,r)  
motion_id2 = lebai.movel(cartesian_pose,a,v,t,r)
直线匀速运动
不指定位置，在指定参考坐标系下，按照速度矢量定速运动，运动多久根据运动时间参数而定，默认t = 0，一直运动到限位。
收到其他运动指令后，会立即终止当前指令，并执行新运动指令。
motion_id = lebai.speedl(a, v, t,frame)
参数介绍：

参数	类型	说明
a	int	空间加速度 (m/s2)
v	dict	各个方向的速度 (m/s) 。如{'x': 0.01, 'y': 0, 'z': 0, 'rz': 0, 'ry':0, 'rx':0}
t	int	运动时间 (s)。可空，默认t = 0，一直运动到限位
frame	dict	运动坐标参考系。可空，默认基座方向
返回值：int类型。返回运动指令id。

注意

注意：速度参数是列表，代表沿着参考坐标系的各个方向的速度。

使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 

a = 2 #空间加速度 (m/s2)
v = {'x': 0.1, 'y': 0, 'z': 0, 'rz': 0, 'ry':0, 'rx':0}| #空间速度 （m/s）
t = 0.2   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效

frame1 = {'x' : 0, 'y' : 0, 'z' : 0, 'rz' : 0, 'ry' : 0, 'rx' : 0} 
frame2 = {'x' : 0, 'y' : 0, 'z' : 0, 'rz' : 1.57, 'ry' : 0, 'rx' : 0} 

motion_id1 = lebai.speedl(a,v,t,frame1)  #沿着基坐标的 x轴方向，以0.1m/s速度和2m/s2加速度运动0.2s

motion_id2 = lebai.speedl(a,v,t,frame2) #坐标参考系非机器基座的基坐标，是新的坐标系，沿着新坐标系的x轴方向运动，相当于沿着原来基坐标的y轴方向运动
圆弧运动
在工具空间内进行圆弧运动，路径为以当前位置、via 和 p 三点组成的唯一圆。沿着圆弧运动一定的弧度。

motion_id = lebai.movec(via, p, rad, a, v, t, r)
参数介绍：

参数	类型	说明
via	dict	途径位置
p	dict	目标位置
rad	int	路径圆弧的弧度 (rad) 。用于指定圆弧运动的弧度大小。
特殊且默认地，当 rad = 0 表示运动到 p 作为终点。
如果 rad > 0，则表示走一个圆弧运动轨迹，途径 via 和 p，并旋转对应的 rad。
如果 rad < 0，则表示反方向走圆弧运动轨迹，via 和 p 在此模式下不一定经过。
a	int	工具空间加速度 (m/s2)
v	int	工具空间速度 (m/s)
t	int	运动时间 (s)
r	int	运动轨迹交融半径 (m)
返回值：int类型。返回运动指令id。

注意

如果三点位于一条直线上无法画圆，或者点之间距离过小以至于唯一圆过大或过小，命令均将执行失败。
执行完圆弧运动的机器人姿态与 p 一致，与 rad 无关。
使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
import math
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False)

cartesian_pose = {'x' : 0.3, 'y' : 0, 'z' : 0.2, 'rz' : 0, 'ry' : 0, 'rx' : 1.57}#起始点
a = 1 #关节加速度 (rad/s2)
v = 0.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id  = lebai.movej(cartesian_pose,a,v,t,r)
 
via = {'x' : 0.35, 'y' : -0.05, 'z' : 0.2, 'rz' : 0, 'ry' : 0, 'rx' : 1.57} #途径点
p = {'x' : 0.4, 'y' : 0, 'z' : 0.2, 'rz' : 0, 'ry' : 0, 'rx' : 1.57} #目标点
rad1 = math.pi  #180度圆弧
a = 1  
v = 0.5  
t = 0    
r = 0.5  
motion_id2 = lebai.movec(via, p, rad, a, v, t, r)

lebai.movej(cartesian_pose,a,v,t,r) 
rad2 = 2*math.pi  #360度圆弧
motion_id3 = lebai.movec(via, p, rad2, a, v, t, r)

## 等待运动完成
lebai.wait_move(motion_id)
参数介绍：

参数	类型	说明
motion_id	int	运动指令返回的motion_id，等待对应的运动指令执行完成。可选参数，默认为0，等待全部运动执行完成
返回值：无返回值。

使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
 
joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id = lebai.movej(joint_pose,a,v,t,r)  
lebai.wait_move(motion_id)


## 获取运动状态
move_state = lebai.get_motion_state(motion_id)
参数介绍：

参数	类型	说明
motion_id	int	运动指令返回的motion_id
返回值：string 类型。返回运动状态: "WAIT"排队中；"RUNNING"运动中；"FINISHED"已完成。

使用示例：

import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False)

joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id = lebai.movej(joint_pose,a,v,t,r)  
move_state = lebai.get_motion_state(motion_id)
print(move_state)
获取正在执行的运动 ID
motion_id = lebai.get_running_motion()
返回值: int 类型。返回正在执行的运动的motion_id。
使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False)
 
joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id = lebai.movej(joint_pose,a,v,t,r)  
print(motion_id)
running_motion_id = lebai.get_running_motion()
print(running_motion_id)
暂停运动
暂停所有运动。不影响任务运行状态。

lebai.pause_move()
返回值：无返回值。
注意

如果有调用任务场景，暂停运动后，场景中的其他逻辑能够继续执行，场景可能代码逻辑执行完毕，动作还没执行。

使用示例：
import lebai_sdk
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145"
lebai = lebai_sdk.connect(robot_ip, False) 
 
joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id = lebai.movej(joint_pose,a,v,t,r)  
print(motion_id)
lebai.pause_move()
恢复运动
方法：lebai.resume_move()
恢复所有运动。不影响任务运行状态。
返回值：无返回值。
使用示例：
import lebai_sdk
import time
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
 
joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id = lebai.movej(joint_pose,a,v,t,r)  
print(motion_id)
lebai.pause_move()
print('暂停中')
time.sleep(3)
lebai.resume_move()
停止运动
停止正在排队执行的所有运动，但无法取消后续新发的运动指令。

lebai.stop_move()
返回值：无返回值。
使用示例：
import lebai_sdk
import time
lebai_sdk.init()
import nest_asyncio
nest_asyncio.apply()
robot_ip = "192.168.4.145" 
lebai = lebai_sdk.connect(robot_ip, False) 
 
joint_pose = [0,-1.05,1.05,0,1.57,0] #目标位姿关节数据
cartesian_pose = {'x' : -0.383, 'y' : -0.121, 'z' : 0.36, 'rz' : -1.57, 'ry' : 0, 'rx' : 1.57}#目标位姿笛卡尔数据
a = 5 #关节加速度 (rad/s2)
v = 1.5 #关节速度 (rad/s)
t = 0   #运动时间 (s)。 当 t > 0 时，参数速度 v 和加速度 a 无效
r = 0.5   #交融半径 (m)。用于指定路径的平滑效果
motion_id = lebai.movej(joint_pose,a,v,t,r)  
print(motion_id)
lebai.stop_move() #停止已经发出的运动指令
time.sleep(3)
motion_id = lebai.movej(cartesian_pose,a,v,t,r)  #这条运动指令会继续执行
print(motion_id)