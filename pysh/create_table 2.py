import mysql.connector
import os

# 数据库配置
db_config = {
    'host': '192.168.101.251',
    'user': 'root',
    'password': 'BigData#123..',
    'database': 'sdashboard',
    'port': 6666
}

try:
    # 连接到数据库
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    # 读取sql文件
    with open('create_chat_history_table.sql', 'r', encoding='utf-8') as file:
        sql_script = file.read()
    
    # 执行sql脚本
    cursor.execute(sql_script)
    
    # 提交事务
    connection.commit()
    
    print("chat_history表创建成功！")
    
except mysql.connector.Error as err:
    print(f"数据库错误: {err}")
except Exception as e:
    print(f"其他错误: {e}")
finally:
    # 关闭连接
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("数据库连接已关闭")