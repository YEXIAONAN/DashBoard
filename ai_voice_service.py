"""
AI Voice Service - FastAPI Backend
独立运行的语音助手后端服务
"""
import os
import base64
import tempfile
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

# ==================== 配置常量 ====================
OLLAMA_HOST = "http://172.16.4.181:11434"
OLLAMA_MODEL = "qwen2.5:7b"
ASR_HOST = "http://127.0.0.1:9001"
TTS_HOST = "http://127.0.0.1:9002"
SERVICE_PORT = 8001

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
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"audio": ("audio.wav", audio_bytes, "audio/wav")}
            response = await client.post(f"{ASR_HOST}/transcribe", files=files)
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR 失败: {str(e)}")

# ==================== Ollama LLM ====================
async def chat_with_ollama(text: str) -> str:
    """与 Ollama 对话"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": text,
                "stream": False
            }
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama 失败: {str(e)}")

# ==================== TTS 服务 ====================
async def text_to_speech(text: str) -> bytes:
    """文字转语音"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"text": text}
            response = await client.post(f"{TTS_HOST}/synthesize", json=payload)
            response.raise_for_status()
            return response.content
    except Exception as e:
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
        # 1. 获取输入文本
        input_text = text or ""
        
        if audio:
            audio_bytes = await audio.read()
            asr_text = await transcribe_audio(audio_bytes)
            input_text = asr_text if asr_text else input_text
        
        if not input_text:
            raise HTTPException(status_code=400, detail="需要提供文本或音频")
        
        # 2. LLM 生成回复
        reply_text = await chat_with_ollama(input_text)
        
        # 3. TTS 生成语音
        audio_bytes = await text_to_speech(reply_text)
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        return {
            "text": reply_text,
            "audio": audio_base64
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
