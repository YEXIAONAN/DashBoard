import time
import lebai_sdk

# 初始化SDK
lebai_sdk.init()

def main():
    robot_ip = "192.168.101.147"
    lebai = lebai_sdk.connect(robot_ip, False)
    lebai.start_sys()  # 启动手臂

    # 进入示教模式
    lebai.teach_mode()
    print("已进入示教模式")

    try:
        while True:
            # 获取手臂当前运动数据
            status_dic = lebai.get_kin_data()

            # 获取并打印反馈关节位置
            joint_pose = status_dic['actual_joint_pose']
            print('反馈关节位置:', joint_pose)

            # 模拟目标位姿设置
            pos_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]  # 示例值
            target_pose = {
                'x': pos_values[0], 'y': pos_values[1], 'z': pos_values[2],
                'rz': pos_values[3], 'ry': pos_values[4], 'rx': pos_values[5]
            }
            print('目标位姿:', target_pose)

            # 等待一段时间再继续循环，模拟实时获取数据
            time.sleep(1)
    except KeyboardInterrupt:
        lebai.end_teach_mode()  # 退出示教模式
        print("已退出示教模式")

# 运行主函数
main()