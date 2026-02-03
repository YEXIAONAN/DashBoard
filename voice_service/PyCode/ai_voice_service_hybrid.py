"""
AI Voice Service - 混合版本 (Hybrid Version)
中文/英文: Coqui TTS (XTTS v2) - 完全离线
越南语: Facebook MMS-TTS - 完全离线
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

# TTS 引擎配置
# 中文/英文使用 XTTS v2，越南语使用 MMS-TTS
XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
XTTS_SPEAKER = "Claribel Dervla"  # 默认说话人

# MMS-TTS 模型（仅越南语）
MMS_MODEL_VI = "facebook/mms-tts-vie"

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI Voice Service - Hybrid (Chinese/English: XTTS, Vietnamese: MMS)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全局变量（延迟加载）====================
whisper_model = None
xtts_model = None
mms_model_vi = None

def load_whisper():
    """延迟加载 Whisper 模型"""
    global whisper_model
    if whisper_model is None:
        try:
            import whisper
            logger.info(f"加载 Whisper 模型: {WHISPER_MODEL}")
            whisper_model = whisper.load_model(WHISPER_MODEL)
            logger.info("✅ Whisper 模型加载成功")
        except Exception as e:
            logger.error(f"Whisper 模型加载失败: {e}")
            raise
    return whisper_model

def load_xtts():
    """延迟加载 XTTS v2 模型（中文/英文）"""
    global xtts_model
    if xtts_model is None:
        try:
            from TTS.api import TTS
            logger.info(f"加载 XTTS v2 模型: {XTTS_MODEL}")
            xtts_model = TTS(model_name=XTTS_MODEL)
            logger.info("✅ XTTS v2 模型加载成功")
        except Exception as e:
            logger.error(f"XTTS v2 模型加载失败: {e}")
            raise
    return xtts_model

def load_mms_vi():
    """延迟加载 MMS-TTS 越南语模型"""
    global mms_model_vi
    if mms_model_vi is None:
        try:
            from transformers import VitsModel, AutoTokenizer
            logger.info(f"加载 MMS-TTS 越南语模型: {MMS_MODEL_VI}")
            model = VitsModel.from_pretrained(MMS_MODEL_VI)
            tokenizer = AutoTokenizer.from_pretrained(MMS_MODEL_VI)
            mms_model_vi = {"model": model, "tokenizer": tokenizer}
            logger.info("✅ MMS-TTS 越南语模型加载成功")
        except Exception as e:
            logger.error(f"MMS-TTS 越南语模型加载失败: {e}")
            raise
    return mms_model_vi

# ==================== ASR 服务（本地 Whisper）====================
async def transcribe_audio(audio_bytes: bytes, language: str = "zh") -> str:
    """音频转文字 - 使用本地 Whisper"""
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
            # 使用 ffmpeg 转换为 WAV
            if not os.path.exists(FFMPEG_EXE):
                ffmpeg_cmd = "ffmpeg"
            else:
                ffmpeg_cmd = FFMPEG_EXE
            
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
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"ffmpeg 转换失败: {result.stderr.decode()}")
                raise Exception("音频格式转换失败")
            
            logger.info(f"音频转换成功: {output_path}")
            
            # 读取 WAV 文件
            import wave
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

# ==================== TTS 服务（混合模式）====================
async def text_to_speech(text: str, language: str = "zh") -> bytes:
    """文字转语音 - 混合模式
    
    中文/英文: XTTS v2
    越南语: MMS-TTS
    """
    try:
        if language == "vi":
            # 越南语使用 MMS-TTS
            return await text_to_speech_mms(text)
        else:
            # 中文/英文使用 XTTS v2
            return await text_to_speech_xtts(text, language)
    except Exception as e:
        logger.error(f"TTS 失败: {str(e)}", exc_info=True)
        logger.warning("TTS 失败，返回空音频")
        return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'

async def text_to_speech_xtts(text: str, language: str = "zh") -> bytes:
    """使用 XTTS v2 合成语音（中文/英文）"""
    try:
        logger.info(f"开始合成语音 (XTTS v2): {text[:50]}..., 语言: {language}")
        
        tts = load_xtts()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # 生成语音
            tts.tts_to_file(
                text=text,
                speaker=XTTS_SPEAKER,
                language=language,
                file_path=tmp_path
            )
            
            # 读取生成的音频
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            logger.info(f"✅ 语音合成完成 (XTTS v2): {len(audio_data)} bytes")
            return audio_data
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"XTTS v2 失败: {str(e)}", exc_info=True)
        raise

async def text_to_speech_mms(text: str) -> bytes:
    """使用 MMS-TTS 合成越南语语音"""
    try:
        import torch
        import scipy.io.wavfile
        
        logger.info(f"开始合成语音 (MMS-TTS): {text[:50]}..., 语言: vi")
        
        mms = load_mms_vi()
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
            # 保存为 WAV 文件
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
        raise

# ==================== Ollama LLM ====================
async def chat_with_ollama(text: str, max_retries: int = 3) -> str:
    """与 Ollama 对话（带重试机制）"""
    import asyncio
    
    for attempt in range(max_retries):
        try:
            logger.info(f"发送到 Ollama (尝试 {attempt + 1}/{max_retries}): {text[:50]}...")
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "model": OLLAMA_MODEL,
                    "prompt": text,
                    "stream": False
                }
                response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
                response.raise_for_status()
                result = response.json()
                reply = result.get("response", "")
                logger.info(f"✅ Ollama 回复成功: {reply[:50]}...")
                return reply
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 502:
                logger.warning(f"⚠️ Ollama 502 错误 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # 等待1秒后重试
                    continue
            logger.error(f"Ollama HTTP 错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")
        except Exception as e:
            logger.error(f"Ollama 失败: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")
    
    raise HTTPException(status_code=500, detail="AI 对话失败: 超过最大重试次数")

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
    """流式对话接口（带重试机制）"""
    import asyncio
    
    try:
        logger.info(f"收到流式对话请求: {text[:50]}..., 语言: {language}")
        
        async def generate():
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    full_text = ""
                    
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        payload = {
                            "model": OLLAMA_MODEL,
                            "prompt": text,
                            "stream": True
                        }
                        
                        logger.info(f"连接 Ollama (尝试 {attempt + 1}/{max_retries})...")
                        
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
                                            logger.info(f"✅ 流式输出完成，完整文本长度: {len(full_text)} 字符")
                                            logger.info(f"开始生成语音，语言: {language}...")
                                            audio_bytes = await text_to_speech(full_text, language)
                                            logger.info(f"语音生成完成，大小: {len(audio_bytes)} bytes")
                                            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                                            yield f"data: {json.dumps({'audio': audio_base64, 'done': True})}\n\n"
                                            return  # 成功完成，退出
                                    except json.JSONDecodeError:
                                        continue
                    
                    return  # 成功完成
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 502:
                        logger.warning(f"⚠️ Ollama 502 错误 (尝试 {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            yield f"data: {json.dumps({'info': f'连接失败，正在重试 ({attempt + 2}/{max_retries})...'})}\n\n"
                            await asyncio.sleep(1)
                            continue
                    logger.error(f"流式对话失败: {str(e)}")
                    yield f"data: {json.dumps({'error': f'AI 服务暂时不可用，请稍后重试'})}\n\n"
                    return
                    
                except Exception as e:
                    logger.error(f"流式对话失败: {str(e)}")
                    if attempt < max_retries - 1:
                        yield f"data: {json.dumps({'info': f'连接失败，正在重试 ({attempt + 2}/{max_retries})...'})}\n\n"
                        await asyncio.sleep(1)
                        continue
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    return
            
            # 所有重试都失败
            yield f"data: {json.dumps({'error': 'AI 服务连接失败，请检查网络或稍后重试'})}\n\n"
        
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
        
        audio_bytes = await text_to_speech(reply_text, language)
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
        "tts": {
            "zh": "XTTS v2 (Coqui TTS)",
            "en": "XTTS v2 (Coqui TTS)",
            "vi": "Facebook MMS-TTS"
        },
        "supported_languages": ["zh", "en", "vi"],
        "mode": "完全离线 / Fully Offline (Hybrid)"
    }

@app.on_event("startup")
async def startup_event():
    """启动时预加载模型"""
    logger.info("=" * 60)
    logger.info("AI 语音助手服务启动中（混合模式 - Hybrid）...")
    logger.info(f"Ollama: {OLLAMA_HOST}")
    logger.info(f"模型: {OLLAMA_MODEL}")
    logger.info(f"Whisper: {WHISPER_MODEL}")
    logger.info("TTS 引擎:")
    logger.info("  - 中文/英文: XTTS v2 (Coqui TTS)")
    logger.info("  - 越南语: Facebook MMS-TTS")
    logger.info("=" * 60)
    
    try:
        logger.info("预加载 Whisper 模型...")
        load_whisper()
        logger.info("预加载 XTTS v2 模型...")
        load_xtts()
        logger.info("预加载 MMS-TTS 越南语模型...")
        load_mms_vi()
        logger.info("✅ 所有模型加载完成")
    except Exception as e:
        logger.warning(f"预加载失败，将在首次请求时加载: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
