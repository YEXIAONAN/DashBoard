"""
AI Voice Service - MMS-TTS 版本
使用 Facebook MMS-TTS 支持中文、英文、越南语
完全离线运行
"""
import os
import base64
import tempfile
import logging
import json
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import uvicorn

# ==================== 设置 ffmpeg 路径到环境变量 ====================
FFMPEG_BIN_PATH = r"C:\ProgramData\chocolatey\bin"
FFMPEG_EXE = os.path.join(FFMPEG_BIN_PATH, "ffmpeg.exe")

if os.path.exists(FFMPEG_BIN_PATH):
    os.environ["PATH"] = FFMPEG_BIN_PATH + os.pathsep + os.environ.get("PATH", "")
    print(f"✓ 已添加 ffmpeg 路径到 PATH: {FFMPEG_BIN_PATH}")

if os.path.exists(FFMPEG_EXE):
    os.environ["FFMPEG_BINARY"] = FFMPEG_EXE
    print(f"✓ 设置 FFMPEG_BINARY: {FFMPEG_EXE}")

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

# Whisper 模型大小
WHISPER_MODEL = "small"

# TTS 引擎：使用 MMS-TTS
TTS_ENGINE = "mms"

# MMS-TTS 模型映射
MMS_MODELS = {
    "zh": "facebook/mms-tts-yue",  # 中文（粤语 - Cantonese，因为 cmn 有认证问题）
    "en": "facebook/mms-tts-eng",  # 英文
    "vi": "facebook/mms-tts-vie"   # 越南语
}

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI Voice Service - MMS-TTS (Vietnamese Support)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全局变量（延迟加载）====================
whisper_model = None
mms_models = {}  # 缓存已加载的模型

def load_whisper():
    """延迟加载 Whisper 模型"""
    global whisper_model
    if whisper_model is None:
        try:
            import whisper
            logger.info(f"加载 Whisper 模型: {WHISPER_MODEL}")
            whisper_model = whisper.load_model(WHISPER_MODEL)
            logger.info("Whisper 模型加载成功")
        except Exception as e:
            logger.error(f"Whisper 模型加载失败: {e}")
            raise
    return whisper_model

def load_mms_model(language: str):
    """延迟加载 MMS-TTS 模型"""
    global mms_models
    
    if language not in mms_models:
        try:
            from transformers import VitsModel, AutoTokenizer
            import torch
            
            model_name = MMS_MODELS.get(language)
            if not model_name:
                raise ValueError(f"不支持的语言: {language}")
            
            logger.info(f"加载 MMS-TTS 模型: {model_name}")
            
            # 加载模型和 tokenizer
            model = VitsModel.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            mms_models[language] = {
                "model": model,
                "tokenizer": tokenizer
            }
            
            logger.info(f"✅ MMS-TTS 模型加载成功: {language}")
            
        except Exception as e:
            logger.error(f"MMS-TTS 模型加载失败 ({language}): {e}")
            raise
    
    return mms_models[language]

# ==================== ASR 服务（本地 Whisper）====================
async def transcribe_audio(audio_bytes: bytes, language: str = "zh") -> str:
    """音频转文字 - 使用本地 Whisper
    
    Args:
        audio_bytes: 音频数据
        language: 语言代码 (zh=中文, en=英文, vi=越南语)
    """
    try:
        import subprocess
        import numpy as np
        
        model = load_whisper()
        
        logger.info(f"开始识别音频: {len(audio_bytes)} bytes, 语言: {language}")
        
        # 保存原始音频到临时文件
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file:
            input_file.write(audio_bytes)
            input_path = input_file.name
        
        # 输出 WAV 文件路径
        output_path = input_path.replace(".webm", ".wav")
        
        try:
            # 检查 ffmpeg 是否存在
            if not os.path.exists(FFMPEG_EXE):
                ffmpeg_cmd = "ffmpeg"
                logger.warning(f"ffmpeg 不在 {FFMPEG_EXE}，尝试使用系统 PATH")
            else:
                ffmpeg_cmd = FFMPEG_EXE
            
            # 使用 ffmpeg 转换为 WAV
            cmd = [
                ffmpeg_cmd,
                "-i", input_path,
                "-ar", "16000",
                "-ac", "1",
                "-acodec", "pcm_s16le",
                "-f", "wav",
                "-y",
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg 转换失败: {result.stderr.decode()}")
                raise Exception("音频格式转换失败")
            
            logger.info(f"音频转换成功: {output_path}")
            
            # 读取 WAV 文件
            import wave
            import numpy as np
            
            with wave.open(output_path, 'rb') as wav_file:
                audio_data = wav_file.readframes(wav_file.getnframes())
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # 根据语言设置提示词
            language_prompts = {
                "zh": "以下是普通话的句子。",
                "en": "The following is in English.",
                "vi": "Sau đây là tiếng Việt."
            }
            initial_prompt = language_prompts.get(language, "")
            
            # 使用 Whisper 识别
            whisper_result = model.transcribe(
                audio_array, 
                language=language,
                fp16=False,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                condition_on_previous_text=False,
                initial_prompt=initial_prompt
            )
            text = whisper_result["text"]
            logger.info(f"识别结果: {text}")
            return text.strip()
            
        finally:
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
                
    except Exception as e:
        logger.error(f"ASR 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")

# ==================== TTS 服务（MMS-TTS）====================
async def text_to_speech_mms(text: str, language: str = "zh") -> bytes:
    """文字转语音 - 使用 MMS-TTS（支持越南语）
    
    Args:
        text: 要合成的文本
        language: 语言代码 (zh=中文, en=英文, vi=越南语)
    """
    try:
        import torch
        import scipy.io.wavfile
        
        logger.info(f"开始合成语音 (MMS-TTS): {text[:50]}..., 语言: {language}")
        
        # 加载对应语言的模型
        mms = load_mms_model(language)
        model = mms["model"]
        tokenizer = mms["tokenizer"]
        
        # Tokenize 文本
        inputs = tokenizer(text, return_tensors="pt")
        
        # 生成语音
        with torch.no_grad():
            output = model(**inputs).waveform
        
        # 转换为 numpy 数组
        audio_array = output.squeeze().cpu().numpy()
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # 保存为 WAV 文件（采样率 16000）
            scipy.io.wavfile.write(tmp_path, rate=16000, data=audio_array)
            
            # 读取生成的音频
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            logger.info(f"✅ 语音合成完成 (MMS-TTS): {len(audio_data)} bytes")
            return audio_data
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"MMS-TTS 失败: {str(e)}", exc_info=True)
        # 返回空音频
        logger.warning("TTS 失败，返回空音频")
        return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'

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

# ==================== 主接口 ====================
@app.post("/transcribe")
async def transcribe_only(
    audio: UploadFile = File(...),
    language: str = Form("zh")
):
    """仅语音识别接口"""
    try:
        logger.info(f"收到语音识别请求，语言: {language}")
        audio_bytes = await audio.read()
        logger.info(f"音频大小: {len(audio_bytes)} bytes")
        
        text = await transcribe_audio(audio_bytes, language)
        
        return {"text": text}
    
    except Exception as e:
        logger.error(f"语音识别失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-stream")
async def chat_stream(
    text: str = Form(...),
    language: str = Form("zh")
):
    """流式对话接口"""
    try:
        logger.info(f"收到流式对话请求: {text[:50]}..., 语言: {language}")
        
        async def generate():
            try:
                full_text = ""
                
                async with httpx.AsyncClient(timeout=120.0) as client:
                    payload = {
                        "model": OLLAMA_MODEL,
                        "prompt": text,
                        "stream": True
                    }
                    
                    async with client.stream("POST", f"{OLLAMA_HOST}/api/generate", json=payload) as response:
                        response.raise_for_status()
                        
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    data = json.loads(line)
                                    if "response" in data:
                                        chunk_text = data["response"]
                                        full_text += chunk_text
                                        yield f"data: {json.dumps({'text': chunk_text})}\n\n"
                                    
                                    if data.get("done", False):
                                        logger.info(f"流式输出完成，完整文本长度: {len(full_text)} 字符")
                                        logger.info(f"开始生成语音，语言: {language}...")
                                        audio_bytes = await text_to_speech_mms(full_text, language)
                                        logger.info(f"语音生成完成，大小: {len(audio_bytes)} bytes")
                                        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                                        yield f"data: {json.dumps({'audio': audio_base64, 'done': True})}\n\n"
                                        break
                                except json.JSONDecodeError:
                                    continue
                        
            except Exception as e:
                logger.error(f"流式对话失败: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"流式对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    language: str = Form("zh")
):
    """统一聊天接口"""
    try:
        logger.info(f"收到请求 - text: {text}, audio: {audio is not None}, language: {language}")
        
        input_text = text or ""
        recognized_text = ""
        
        if audio:
            audio_bytes = await audio.read()
            logger.info(f"音频大小: {len(audio_bytes)} bytes")
            asr_text = await transcribe_audio(audio_bytes, language)
            input_text = asr_text if asr_text else input_text
            recognized_text = asr_text
        
        if not input_text:
            raise HTTPException(status_code=400, detail="需要提供文本或音频")
        
        logger.info(f"处理输入: {input_text}")
        
        reply_text = await chat_with_ollama(input_text)
        
        audio_bytes = await text_to_speech_mms(reply_text, language)
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        logger.info("请求处理成功")
        
        return {
            "text": reply_text,
            "audio": audio_base64,
            "recognized_text": recognized_text
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
        "asr": "openai-whisper (local)",
        "tts": "Facebook MMS-TTS (fully offline)",
        "supported_languages": ["zh", "en", "vi"],
        "mode": "完全离线 / Fully Offline"
    }

@app.on_event("startup")
async def startup_event():
    """启动时预加载模型"""
    logger.info("=" * 50)
    logger.info("AI 语音助手服务启动中（MMS-TTS - 支持越南语）...")
    logger.info(f"Ollama: {OLLAMA_HOST}")
    logger.info(f"模型: {OLLAMA_MODEL}")
    logger.info(f"Whisper: {WHISPER_MODEL}")
    logger.info(f"TTS 引擎: {TTS_ENGINE}")
    logger.info("=" * 50)
    
    try:
        logger.info("预加载 Whisper 模型...")
        load_whisper()
        logger.info("预加载 MMS-TTS 模型...")
        # 预加载所有语言的模型
        for lang in ["zh", "en", "vi"]:
            logger.info(f"  加载 {lang} 模型...")
            load_mms_model(lang)
        logger.info("✅ 所有模型加载完成")
    except Exception as e:
        logger.warning(f"预加载失败，将在首次请求时加载: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
