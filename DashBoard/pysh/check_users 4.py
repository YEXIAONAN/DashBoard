import os
import sys
import django
import random

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DashBoard.settings')
django.setup()

from main.models import Users

# 百家姓列表（常见姓氏）
common_surnames = [
    '李', '王', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
    '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
    '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
    '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕',
    '苏', '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎'
]

# 男性常用名字
male_names = [
    '伟', '强', '磊', '军', '勇', '杰', '涛', '明', '超', '亮',
    '刚', '平', '辉', '鹏', '华', '建', '志', '大', '博', '鑫',
    '宇航', '浩然', '子轩', '博文', '天宇', '俊杰', '晨曦', '泽宇', '文博', '浩宇',
    '子豪', '昊然', '志强', '建国', '建军', '志明', '文杰', '建华', '永强', '志伟'
]

# 女性常用名字
female_names = [
    '芳', '娜', '敏', '静', '丽', '红', '燕', '艳', '娟', '萍',
    '英', '慧', '婷', '秀', '珍', '雪', '琳', '丹', '玲', '莹',
    '诗涵', '欣怡', '雨婷', '雅琪', '梦琪', '嘉怡', '子怡', '雨欣', '心怡', '文静',
    '美琳', '慧敏', '丽娜', '秀英', '玉兰', '桂英', '秀兰', '春梅', '雪梅', '红梅'
]

# 生成随机中文姓名的函数
def generate_chinese_name(gender):
    surname = random.choice(common_surnames)
    
    if gender == '男':
        # 70%概率生成两字名，30%概率生成三字名
        if random.random() < 0.7:
            given_name = random.choice(male_names[:20])  # 单字名
        else:
            given_name = random.choice(male_names[20:])  # 双字名
    elif gender == '女':
        # 70%概率生成两字名，30%概率生成三字名
        if random.random() < 0.7:
            given_name = random.choice(female_names[:20])  # 单字名
        else:
            given_name = random.choice(female_names[20:])  # 双字名
    else:
        # 默认男性名字
        if random.random() < 0.7:
            given_name = random.choice(male_names[:20])
        else:
            given_name = random.choice(male_names[20:])
    
    return surname + given_name

# 查询所有用户
users = Users.objects.all()
print(f'当前用户数量: {users.count()}')
print('\n前5个用户信息:')
for user in users[:5]:
    print(f'用户ID: {user.user_id}, 姓名: {user.name}, 性别: {user.gender}')

# 为没有姓名的用户添加示例数据
print('\n为没有姓名的用户添加示例数据...')
for user in users:
    if not user.name or user.name.startswith('张') or user.name.startswith('李') or user.name.startswith('用户'):
        new_name = generate_chinese_name(user.gender)
        user.name = new_name
        user.save()
        print(f'已为用户 {user.user_id} 设置姓名: {user.name}')

print('\n更新后的用户信息:')
for user in users[:5]:
    print(f'用户ID: {user.user_id}, 姓名: {user.name}, 性别: {user.gender}')