"""
AI Voice Service - 完全离线版本
使用本地 ASR (faster-whisper) 和 TTS (pyttsx3)
"""
import os
import base64
import tempfile
import logging
import io
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================
OLLAMA_HOST = "http://172.16.4.181:11434"
OLLAMA_MODEL = "qwen2.5:7b"
SERVICE_PORT = 8001

# Whisper 模型大小: tiny, base, small, medium, large
WHISPER_MODEL = "base"  # base 模型平衡速度和准确度

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI Voice Service - Offline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全局变量（延迟加载）====================
whisper_model = None
tts_engine = None

def load_whisper():
    """延迟加载 Whisper 模型"""
    global whisper_model
    if whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            logger.info(f"加载 Whisper 模型: {WHISPER_MODEL}")
            whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
            logger.info("Whisper 模型加载成功")
        except Exception as e:
            logger.error(f"Whisper 模型加载失败: {e}")
            raise
    return whisper_model

def load_tts():
    """延迟加载 TTS 引擎"""
    global tts_engine
    if tts_engine is None:
        try:
            import pyttsx3
            logger.info("初始化 TTS 引擎")
            tts_engine = pyttsx3.init()
            # 设置语速和音量
            tts_engine.setProperty('rate', 150)  # 语速
            tts_engine.setProperty('volume', 0.9)  # 音量
            logger.info("TTS 引擎初始化成功")
        except Exception as e:
            logger.error(f"TTS 引擎初始化失败: {e}")
            raise
    return tts_engine

# ==================== ASR 服务（本地 Whisper）====================
async def transcribe_audio(audio_bytes: bytes) -> str:
    """音频转文字 - 使用本地 Whisper"""
    try:
        model = load_whisper()
        
        # 保存临时音频文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            logger.info(f"开始识别音频: {len(audio_bytes)} bytes")
            segments, info = model.transcribe(tmp_path, language="zh")
            
            # 合并所有片段
            text = " ".join([segment.text for segment in segments])
            logger.info(f"识别结果: {text}")
            return text.strip()
        finally:
            # 删除临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"ASR 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")

# ==================== Ollama LLM ====================
async def chat_with_ollama(text: str) -> str:
    """与 Ollama 对话"""
    try:
        logger.info(f"发送到 Ollama: {text[:50]}...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": text,
                "stream": False
            }
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            reply = result.get("response", "")
            logger.info(f"Ollama 回复: {reply[:50]}...")
            return reply
    except Exception as e:
        logger.error(f"Ollama 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")

# ==================== TTS 服务（本地 pyttsx3）====================
async def text_to_speech(text: str) -> bytes:
    """文字转语音 - 使用本地 TTS"""
    try:
        engine = load_tts()
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            logger.info(f"开始合成语音: {text[:50]}...")
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            
            # 读取生成的音频
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            logger.info(f"语音合成完成: {len(audio_data)} bytes")
            return audio_data
        finally:
            # 删除临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"TTS 失败: {str(e)}", exc_info=True)
        # 返回空音频而不是失败
        logger.warning("TTS 失败，返回空音频")
        return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'

# ==================== 主接口 ====================
@app.post("/chat")
async def chat(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None)
):
    """
    统一聊天接口
    - text: 文本输入（可选）
    - audio: 音频文件（可选）
    """
    try:
        logger.info(f"收到请求 - text: {text}, audio: {audio is not None}")
        
        # 1. 获取输入文本
        input_text = text or ""
        
        if audio:
            audio_bytes = await audio.read()
            logger.info(f"音频大小: {len(audio_bytes)} bytes")
            asr_text = await transcribe_audio(audio_bytes)
            input_text = asr_text if asr_text else input_text
        
        if not input_text:
            raise HTTPException(status_code=400, detail="需要提供文本或音频")
        
        logger.info(f"处理输入: {input_text}")
        
        # 2. LLM 生成回复
        reply_text = await chat_with_ollama(input_text)
        
        # 3. TTS 生成语音
        audio_bytes = await text_to_speech(reply_text)
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        logger.info("请求处理成功")
        
        return {
            "text": reply_text,
            "audio": audio_base64
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "ollama": OLLAMA_HOST,
        "model": OLLAMA_MODEL,
        "whisper_model": WHISPER_MODEL,
        "asr": "faster-whisper (local)",
        "tts": "pyttsx3 (local)"
    }

@app.on_event("startup")
async def startup_event():
    """启动时预加载模型"""
    logger.info("=" * 50)
    logger.info("AI 语音助手服务启动中...")
    logger.info(f"Ollama: {OLLAMA_HOST}")
    logger.info(f"模型: {OLLAMA_MODEL}")
    logger.info(f"Whisper: {WHISPER_MODEL}")
    logger.info("=" * 50)
    
    # 预加载模型（可选，首次请求时会自动加载）
    try:
        logger.info("预加载 Whisper 模型...")
        load_whisper()
        logger.info("预加载 TTS 引擎...")
        load_tts()
        logger.info("所有模型加载完成")
    except Exception as e:
        logger.warning(f"预加载失败，将在首次请求时加载: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
