# Description: 本地聊天管理
import chat_local
import threading
import time
from chat_mysql import Chat_MySQL

defaule_living_time = 300

# 本地聊天管理, 在一定时间内没有聊天则释放资源
class ChatLocalManage:
    def __init__(self):
        self.chat_exectutor_runing = {}
        self.timer = {}
        self.mysql = Chat_MySQL()

    def chat(self, user_id:int, text: str):
        print("begin chat")
        if user_id not in self.chat_exectutor_runing:
            print("new chat_executor")
            self.chat_exectutor_runing[user_id] = chat_local.chat_furina(user_id, True, self.mysql) # 加载一个对话
        else:
            print("reset timer")
            self.timer[user_id].cancel()
        self.timer[user_id] = threading.Timer(defaule_living_time, self.release_chat_executor, (user_id,))
        ret = self.chat_exectutor_runing[user_id].chat_with_ollama(text)
        self.timer[user_id].start()
        return ret
    
    def release_chat_executor(self, user_id):
        del self.chat_exectutor_runing[user_id]
        del self.timer[user_id]
        print("chat_executor released %d " % user_id)

    def get_new_user_id(self):
        while True:
            temp_id = int(time.time() * 1000) % 1000000000
            if not self.mysql.is_exist(temp_id):
                return temp_id
            
    def release_all_chat_executor(self):
        user_ids = list(self.chat_exectutor_runing.keys())
        for user_id in user_ids:
            self.timer[user_id].cancel()
            self.release_chat_executor(user_id)

if __name__ == "__main__":
    chat_manage = ChatLocalManage()
    print(chat_manage.chat(12, "你还记得我的名字吗?"))
    chat_manage.release_all_chat_executor()
    
