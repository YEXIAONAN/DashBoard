"""
AI Voice Service - FastAPI Backend
独立运行的语音助手后端服务
"""
import os
import base64
import tempfile
import logging
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
OLLAMA_HOST = "http://10.0.0.10:11434"
OLLAMA_MODEL = "qwen2.5:7b"
ASR_HOST = "http://10.0.0.10:9001"
TTS_HOST = "http://10.0.0.10:9002"
SERVICE_PORT = 8001

# 是否启用 ASR/TTS（如果服务未运行，可以禁用）
ENABLE_ASR = False  # 暂时禁用 ASR
ENABLE_TTS = False  # 暂时禁用 TTS

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI Voice Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ASR 服务 ====================
async def transcribe_audio(audio_bytes: bytes) -> str:
    """音频转文字"""
    if not ENABLE_ASR:
        logger.warning("ASR 服务未启用，返回占位文本")
        return "[语音输入]"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"audio": ("audio.wav", audio_bytes, "audio/wav")}
            response = await client.post(f"{ASR_HOST}/transcribe", files=files)
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
    except Exception as e:
        logger.error(f"ASR 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ASR 失败: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Ollama 失败: {str(e)}")

# ==================== TTS 服务 ====================
async def text_to_speech(text: str) -> bytes:
    """文字转语音"""
    if not ENABLE_TTS:
        logger.warning("TTS 服务未启用，返回空音频")
        # 返回一个最小的 WAV 文件头（44字节）
        return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"text": text}
            response = await client.post(f"{TTS_HOST}/synthesize", json=payload)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"TTS 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS 失败: {str(e)}")

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
        "asr_enabled": ENABLE_ASR,
        "tts_enabled": ENABLE_TTS
    }

if __name__ == "__main__":
    logger.info(f"启动服务 - Ollama: {OLLAMA_HOST}, Model: {OLLAMA_MODEL}")
    logger.info(f"ASR: {'启用' if ENABLE_ASR else '禁用'}, TTS: {'启用' if ENABLE_TTS else '禁用'}")
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
