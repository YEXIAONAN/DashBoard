import asyncio
import websockets
import json
import time
import logging
import aiohttp
from datetime import datetime

# 配置日志，添加UTF-8编码支持
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AIHealthKeepAlive:
    def __init__(self, websocket_url, ota_url, device_id="web_keep_alive_client", client_id="keep_alive_client", device_mac="00:11:22:33:44:55"):
        self.websocket_url = websocket_url
        self.ota_url = ota_url
        self.device_id = device_id
        self.client_id = client_id
        self.device_mac = device_mac
        self.websocket = None
        self.is_connected = False
        self.ta_connected = False
        self.keep_alive_interval = 60  # 60秒间隔（1分钟）
        self.ota_keep_alive_interval = 60  # OTA保活间隔60秒（1分钟）
        self.test_message_interval = 60  # 测试消息间隔60秒（1分钟）
        self.max_retries = 3
        self.retry_delay = 5
        self.session = None
        
        # 大模型回复相关功能
        self.message_history = []  # 存储消息历史
        self.audio_buffer_queue = []  # 存储音频数据包
        self.is_processing_audio = False  # 是否正在处理音频
        self.max_audio_buffer_size = 100  # 最大音频缓冲区大小
        
        # 创建消息历史文件
        self.message_history_file = 'message_history.json'
        self.load_message_history()
        
    async def connect_to_server(self):
        """连接到WebSocket服务器"""
        try:
            # 构建连接URL，添加认证参数
            from urllib.parse import urlparse, parse_qs, urlencode
            import urllib.parse
            
            parsed_url = urllib.parse.urlparse(self.websocket_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # 添加认证参数
            query_params['device-id'] = [self.device_id]
            query_params['client-id'] = [self.client_id]
            
            # 重建URL
            new_query = urllib.parse.urlencode(query_params, doseq=True)
            connect_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            logging.info(f"正在连接到服务器: {connect_url}")
            
            # 创建WebSocket连接
            self.websocket = await websockets.connect(
                connect_url,
                ping_interval=None,
                ping_timeout=None,
                close_timeout=1
            )
            
            self.is_connected = True
            logging.info("WebSocket连接成功")
            
            # 发送hello消息
            await self.send_hello_message()
            
            return True
            
        except Exception as e:
            logging.error(f"连接服务器失败: {e}")
            self.is_connected = False
            return False
    
    async def send_hello_message(self):
        """发送hello消息进行初始认证"""
        if not self.is_connected or not self.websocket:
            return False
            
        try:
            # 根据ai_health_advisor.html中的格式发送hello消息
            hello_message = {
                "type": "hello",
                "device_id": self.device_id,
                "device_name": "Python",  # 设备名称
                "device_mac": self.device_mac,  # 设备MAC地址
                "token": "your-token1",  # 认证token
                "features": {
                    "mcp": True
                }
            }
            
            await self.websocket.send(json.dumps(hello_message))
            logging.info(f"发送hello消息: {json.dumps(hello_message)}")
            return True
            
        except Exception as e:
            logging.error(f"发送hello消息失败: {e}")
            return False
    
    async def send_keep_alive_message(self):
        """发送保活消息"""
        if not self.is_connected or not self.websocket:
            return False
            
        try:
            # 根据ai_health_advisor.html中的格式发送保活消息
            # 使用listen类型模拟用户交互，这是服务端期望的格式
            keep_alive_message = {
                "type": "listen",
                "mode": "manual",
                "state": "detect",
                "text": "tts_keep_test"  # 简单的ping消息
            }
            
            await self.websocket.send(json.dumps(keep_alive_message))
            logging.info(f"发送保活消息: {json.dumps(keep_alive_message)}")
            return True
            
        except Exception as e:
            logging.error(f"发送保活消息失败: {e}")
            return False
    
    async def send_test_message(self):
        """发送测试消息，专门用于触发大模型回复"""
        if not self.is_connected or not self.websocket:
            return False
            
        try:
            # 发送一个能够触发大模型回复的测试消息
            test_message = {
                "type": "listen",
                "mode": "manual",
                "state": "detect",
                "text": "tts_keep_test"  # 这个消息应该能够触发大模型回复
            }
            
            await self.websocket.send(json.dumps(test_message))
            logging.info(f"发送测试消息: {json.dumps(test_message)}")
            return True
            
        except Exception as e:
            logging.error(f"发送测试消息失败: {e}")
            return False
    
    async def listen_for_messages(self):
        """监听服务器消息"""
        if not self.is_connected or not self.websocket:
            return
            
        try:
            async for message in self.websocket:
                try:
                    if isinstance(message, str):
                        # 处理文本消息
                        data = json.loads(message)
                        self.handle_server_message(data)
                    else:
                        # 处理二进制消息（音频数据）
                        logging.debug(f"收到二进制消息，长度: {len(message)}")
                        # 调用音频数据处理函数
                        self.process_audio_data(message)
                        
                except json.JSONDecodeError:
                    logging.warning(f"收到非JSON消息: {message}")
                except Exception as e:
                    logging.error(f"处理消息时出错: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logging.info("WebSocket连接已关闭")
            self.is_connected = False
        except Exception as e:
            logging.error(f"监听消息时出错: {e}")
            self.is_connected = False
    
    def load_message_history(self):
        """加载消息历史记录"""
        try:
            import os
            if os.path.exists(self.message_history_file):
                with open(self.message_history_file, 'r', encoding='utf-8') as f:
                    self.message_history = json.load(f)
                logging.info(f"已加载 {len(self.message_history)} 条历史消息")
        except Exception as e:
            logging.warning(f"加载消息历史失败: {e}")
            self.message_history = []
    
    def save_message_history(self):
        """保存消息历史记录"""
        try:
            with open(self.message_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.message_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存消息历史失败: {e}")
    
    def add_message(self, text, is_user=False, msg_type='text'):
        """添加消息到历史记录，类似ai_health_advisor.html中的addMessage功能"""
        import re
        
        # 过滤emoji表情，保持与前端一致
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        filtered_text = emoji_pattern.sub('', text).strip()
        
        message_entry = {
            'timestamp': datetime.now().isoformat(),
            'text': filtered_text,
            'is_user': is_user,
            'msg_type': msg_type,
            'original_text': text
        }
        
        self.message_history.append(message_entry)
        
        # 保持历史记录在合理范围内
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-500:]
        
        # 保存到文件
        self.save_message_history()
        
        # 记录到日志，安全处理Unicode字符
        sender = "用户" if is_user else "AI"
        try:
            logging.info(f"[{sender}] {filtered_text}")
        except UnicodeEncodeError:
            # 如果编码失败，移除特殊字符后记录
            safe_text = filtered_text.encode('ascii', errors='ignore').decode('ascii')
            logging.info(f"[{sender}] {safe_text}")
        
        # 如果是AI回复且过滤后为空，在控制台显示原始内容
        if not is_user and msg_type == 'llm' and not filtered_text:
            print(f"\n[AI回复 - 原始内容]: {text}")
        
        return message_entry
    
    def process_audio_data(self, audio_data):
        """处理音频数据，类似ai_health_advisor.html中的handleBinaryMessage功能"""
        try:
            if len(audio_data) == 0:
                logging.warning("收到空音频数据帧，可能是结束标志")
                # 处理缓冲的音频数据
                if self.audio_buffer_queue:
                    logging.info(f"处理缓冲的音频数据，共 {len(self.audio_buffer_queue)} 个包")
                    self.process_buffered_audio()
                return
            
            # 添加到音频缓冲队列
            self.audio_buffer_queue.append(audio_data)
            
            # 限制缓冲区大小
            if len(self.audio_buffer_queue) > self.max_audio_buffer_size:
                self.audio_buffer_queue = self.audio_buffer_queue[-self.max_audio_buffer_size:]
                logging.warning(f"音频缓冲区已满，丢弃旧数据")
            
            # 如果累积了足够的数据，开始处理
            if len(self.audio_buffer_queue) >= 3 and not self.is_processing_audio:
                self.process_buffered_audio()
                
        except Exception as e:
            logging.error(f"处理音频数据时出错: {e}")
    
    def process_buffered_audio(self):
        """处理缓冲的音频数据"""
        if not self.audio_buffer_queue or self.is_processing_audio:
            return
            
        self.is_processing_audio = True
        try:
            total_size = sum(len(data) for data in self.audio_buffer_queue)
            logging.info(f"开始处理音频数据: {len(self.audio_buffer_queue)} 个包，总大小 {total_size} 字节")
            
            # 这里可以添加音频处理逻辑，如保存到文件或进一步分析
            # 目前只是记录信息
            audio_info = {
                'timestamp': datetime.now().isoformat(),
                'packet_count': len(self.audio_buffer_queue),
                'total_size': total_size,
                'average_packet_size': total_size / len(self.audio_buffer_queue)
            }
            
            # 添加音频消息到历史记录
            self.add_message(
                f"[音频] 收到 {audio_info['packet_count']} 个音频包，总大小 {audio_info['total_size']} 字节",
                is_user=False,
                msg_type='audio'
            )
            
            # 清空缓冲区
            self.audio_buffer_queue.clear()
            
        except Exception as e:
            logging.error(f"处理缓冲音频时出错: {e}")
        finally:
            self.is_processing_audio = False
    
    def handle_server_message(self, message):
        """处理服务器返回的消息，增强版支持大模型回复接收"""
        if isinstance(message, dict):
            msg_type = message.get('type', 'unknown')
            
            if msg_type == 'hello':
                logging.info(f"服务器hello回应: {json.dumps(message)}")
                # 记录连接成功消息
                self.add_message("系统已连接", is_user=False, msg_type='system')
                
            elif msg_type == 'llm':
                # 处理大模型回复
                text = message.get('text', '')
                if text:
                    # 过滤emoji并添加到消息历史
                    self.add_message(text, is_user=False, msg_type='llm')
                    # 直接在控制台输出大模型回复，确保用户能看到
                    print(f"\n=== 大模型回复 ===")
                    print(f"内容: {text}")
                    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"=================\n")
                    # 安全处理Unicode字符，避免GBK编码错误
                    try:
                        logging.info(f"收到大模型回复: {text[:100]}{'...' if len(text) > 100 else ''}")
                    except UnicodeEncodeError:
                        # 如果编码失败，移除特殊字符后记录
                        safe_text = text[:100].encode('ascii', errors='ignore').decode('ascii')
                        logging.info(f"收到大模型回复: {safe_text}{'...' if len(text) > 100 else ''}")
                else:
                    logging.warning("收到空的LLM回复")
                    
            elif msg_type == 'tts':
                # 处理语音合成消息
                state = message.get('state', '')
                if state == 'start':
                    logging.info("服务器开始发送语音数据")
                    self.add_message("[语音] 开始接收语音", is_user=False, msg_type='tts_start')
                elif state == 'stop':
                    logging.info("服务器语音传输结束")
                    self.add_message("[语音] 语音传输结束", is_user=False, msg_type='tts_stop')
                    # 处理剩余的音频数据
                    if self.audio_buffer_queue:
                        self.process_buffered_audio()
                else:
                    logging.info(f"收到TTS消息，状态: {state}")
                    
            elif msg_type == 'stt':
                # 处理语音识别结果
                text = message.get('text', '')
                if text:
                    self.add_message(f"[语音识别] {text}", is_user=True, msg_type='stt')
                    logging.info(f"语音识别结果: {text}")
                
            elif msg_type == 'audio':
                # 处理音频控制消息
                action = message.get('action', '')
                logging.info(f"收到音频控制消息: {action}")
                
            elif msg_type == 'mcp':
                # 处理MCP工具调用消息
                logging.info(f"服务器下发MCP消息: {json.dumps(message)}")
                # 提取有用的信息并记录
                tool = message.get('tool', '')
                content = message.get('content', '')
                if tool or content:
                    mcp_text = f"[MCP工具] {tool}: {content}"
                    self.add_message(mcp_text, is_user=False, msg_type='mcp')
                    
            else:
                logging.info(f"收到其他类型消息: {msg_type} - {json.dumps(message)}")
                # 记录未知类型的消息
                self.add_message(f"[未知消息] {msg_type}: {json.dumps(message)}", is_user=False, msg_type='unknown')
        else:
            logging.warning(f"收到非字典类型消息: {type(message)} - {message}")
    
    async def disconnect(self):
        """断开连接"""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.close()
                logging.info("WebSocket连接已断开")
            except Exception as e:
                logging.error(f"断开连接时出错: {e}")
            finally:
                self.is_connected = False
                self.websocket = None
    
    async def connect_to_ota(self):
        """连接到OTA服务器"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            ota_data = {
                "version": 0,
                "uuid": "",
                "application": {
                    "name": "xiaozhi-web-test",
                    "version": "1.0.0",
                    "compile_time": "2025-04-16 10:00:00",
                    "idf_version": "4.4.3",
                    "elf_sha256": "1234567890abcdef1234567890abcdef1234567890abcdef"
                },
                "ota": {
                    "label": "xiaozhi-web-test",
                },
                "board": {
                    "type": "xiaozhi-web-test",
                    "ssid": "xiaozhi-web-test",
                    "rssi": 0,
                    "channel": 0,
                    "ip": "172.16.4.248",
                    "mac": self.device_mac
                },
                "flash_size": 0,
                "minimum_free_heap_size": 0,
                "mac_address": self.device_mac,
                "chip_model_name": "",
                "chip_info": {
                    "model": 0,
                    "cores": 0,
                    "revision": 0,
                    "features": 0
                },
                "partition_table": [
                    {
                        "label": "",
                        "type": 0,
                        "subtype": 0,
                        "address": 0,
                        "size": 0
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Device-Id': self.device_id,
                'Client-Id': self.client_id
            }
            
            logging.info(f"正在连接到OTA服务器: {self.ota_url}")
            
            async with self.session.post(self.ota_url, json=ota_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"OTA连接成功: {json.dumps(result)}")
                    self.ota_connected = True
                    return True
                else:
                    logging.error(f"OTA连接失败: {response.status} {response.reason}")
                    self.ota_connected = False
                    return False
                    
        except Exception as e:
            logging.error(f"OTA连接错误: {e}")
            self.ota_connected = False
            return False
    
    async def send_ota_keep_alive(self):
        """发送OTA保活消息"""
        if not self.ota_connected or not self.session:
            return False
            
        try:
            # 使用相同的OTA数据格式进行保活
            ota_data = {
                "version": 0,
                "uuid": f"keep_alive_{int(time.time())}",
                "application": {
                    "name": "xiaozhi-web-test",
                    "version": "1.0.0",
                    "compile_time": "2025-04-16 10:00:00",
                    "idf_version": "4.4.3",
                    "elf_sha256": "1234567890abcdef1234567890abcdef1234567890abcdef"
                },
                "ota": {
                    "label": "xiaozhi-web-test",
                },
                "board": {
                    "type": "xiaozhi-web-test",
                    "ssid": "xiaozhi-web-test",
                    "rssi": 0,
                    "channel": 0,
                    "ip": "172.16.4.248",
                    "mac": self.device_mac
                },
                "flash_size": 0,
                "minimum_free_heap_size": 0,
                "mac_address": self.device_mac,
                "chip_model_name": "",
                "chip_info": {
                    "model": 0,
                    "cores": 0,
                    "revision": 0,
                    "features": 0
                },
                "partition_table": [
                    {
                        "label": "",
                        "type": 0,
                        "subtype": 0,
                        "address": 0,
                        "size": 0
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Device-Id': self.device_id,
                'Client-Id': self.client_id
            }
            
            async with self.session.post(self.ota_url, json=ota_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"OTA保活消息发送成功: {json.dumps(result)}")
                    return True
                else:
                    logging.error(f"OTA保活消息发送失败: {response.status} {response.reason}")
                    return False
                    
        except Exception as e:
            logging.error(f"发送OTA保活消息失败: {e}")
            return False
    
    async def disconnect_ota(self):
        """断开OTA连接"""
        if self.session:
            try:
                await self.session.close()
                logging.info("OTA连接已断开")
            except Exception as e:
                logging.error(f"断开OTA连接时出错: {e}")
            finally:
                self.session = None
                self.ota_connected = False
    
    async def run_keep_alive(self):
        """运行保活程序"""
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # 连接WebSocket服务器
                websocket_connected = await self.connect_to_server()
                # 连接OTA服务器
                ota_connected = await self.connect_to_ota()
                
                if not websocket_connected and not ota_connected:
                    retry_count += 1
                    if retry_count < self.max_retries:
                        logging.info(f"所有连接失败，{self.retry_delay}秒后重试 (尝试 {retry_count}/{self.max_retries})")
                        await asyncio.sleep(self.retry_delay)
                    continue
                
                # 重置重试计数
                retry_count = 0
                
                # 启动WebSocket消息监听任务
                listen_task = None
                if websocket_connected:
                    listen_task = asyncio.create_task(self.listen_for_messages())
                
                # 保活消息循环
                # 设置初始时间戳为当前时间，确保连接后等待10秒再发送第一次消息
                websocket_last_keep_alive = time.time() - self.keep_alive_interval + 10
                ota_last_keep_alive = time.time() - self.ota_keep_alive_interval + 10
                test_last_message = time.time() - self.test_message_interval + 10
                
                while self.is_connected or self.ota_connected:
                    try:
                        # 检查是否需要发送WebSocket保活消息
                        current_time = time.time()
                        if self.is_connected and (current_time - websocket_last_keep_alive >= self.keep_alive_interval):
                            if not await self.send_keep_alive_message():
                                logging.error("发送WebSocket保活消息失败")
                                # 不退出循环，继续尝试其他消息
                            else:
                                websocket_last_keep_alive = current_time
                        
                        # 检查是否需要发送OTA保活消息
                        if self.ota_connected and (current_time - ota_last_keep_alive >= self.ota_keep_alive_interval):
                            if not await self.send_ota_keep_alive():
                                logging.error("发送OTA保活消息失败")
                                # OTA连接失败，标记为断开，但不退出循环
                                self.ota_connected = False
                            else:
                                ota_last_keep_alive = current_time
                        
                        # 检查是否需要发送测试消息（用于触发大模型回复）
                        if self.is_connected and (current_time - test_last_message >= self.test_message_interval):
                            if not await self.send_test_message():
                                logging.error("发送测试消息失败")
                                # 不退出循环，继续尝试其他消息
                            else:
                                test_last_message = current_time
                        
                        # 等待1秒后再次检查
                        await asyncio.sleep(1)
                    except asyncio.CancelledError:
                        logging.info("保活程序被取消，正在优雅关闭...")
                        break
                    except websockets.exceptions.ConnectionClosed:
                        logging.warning("WebSocket连接已关闭")
                        self.is_connected = False
                    except Exception as e:
                        logging.error(f"保活消息循环错误: {e}")
                        break
                
                # 取消监听任务
                if listen_task:
                    listen_task.cancel()
                    try:
                        await listen_task
                    except asyncio.CancelledError:
                        pass
                
                # 断开所有连接
                await self.disconnect()
                await self.disconnect_ota()
                
                # 如果是正常退出，不重试
                if retry_count == 0:
                    break
                    
            except Exception as e:
                logging.error(f"运行保活程序时出错: {e}")
                retry_count += 1
                if retry_count < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
        
        logging.info("保活程序已停止")


async def main():
    # 配置参数 - 根据实际情况修改
    WEBSOCKET_URL = "ws://172.16.4.248:8000/xiaozhi/v1/"
    OTA_URL = "http://172.16.4.248:8003/xiaozhi/ota/"
    DEVICE_ID = "keep_alive_device"
    CLIENT_ID = "keep_alive_client"
    DEVICE_MAC = "00:11:22:33:44:66"  # 使用不同的MAC地址避免冲突
    
    logging.info("启动AI健康顾问保活程序")
    logging.info(f"WebSocket服务器地址: {WEBSOCKET_URL}")
    logging.info(f"OTA服务器地址: {OTA_URL}")
    logging.info(f"设备ID: {DEVICE_ID}")
    logging.info(f"客户端ID: {CLIENT_ID}")
    logging.info(f"WebSocket保活间隔: 5秒")
    logging.info(f"OTA保活间隔: 30秒")
    
    # 创建保活实例
    keep_alive = AIHealthKeepAlive(
        websocket_url=WEBSOCKET_URL,
        ota_url=OTA_URL,
        device_id=DEVICE_ID,
        client_id=CLIENT_ID,
        device_mac=DEVICE_MAC
    )
    
    try:
        # 运行保活程序
        await keep_alive.run_keep_alive()
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except asyncio.CancelledError:
        logging.info("程序被取消，正在优雅关闭...")
    except Exception as e:
        logging.error(f"程序运行出错: {e}")
    finally:
        # 确保所有连接被断开
        await keep_alive.disconnect()
        await keep_alive.disconnect_ota()


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())