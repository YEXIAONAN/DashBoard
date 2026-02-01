"""
AI Voice Service - viXTTS 版本
使用 viXTTS 模型支持中文、英文、越南语
完全离线运行
"""
import os
import base64
import tempfile
import logging
import json
import asyncio
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

# TTS 引擎：使用 viXTTS（支持越南语）
TTS_ENGINE = "vixtts"

# viXTTS 模型路径
VIXTTS_MODEL = "capleaf/viXTTS"

# 使用非流式模式（流式模式在某些 Ollama 配置下会返回 502）
USE_STREAMING = False

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI Voice Service - viXTTS (Vietnamese Support)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全局变量（延迟加载）====================
whisper_model = None
vixtts_model = None

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

def load_vixtts():
    """延迟加载 viXTTS 模型"""
    global vixtts_model
    if vixtts_model is None:
        try:
            from TTS.api import TTS
            import torch
            from huggingface_hub import hf_hub_download
            import os
            
            logger.info("初始化 viXTTS 模型")
            logger.info(f"模型: {VIXTTS_MODEL}")
            
            # 添加安全全局变量（兼容 PyTorch 2.6+）
            try:
                from TTS.tts.configs.xtts_config import XttsConfig
                from TTS.tts.models.xtts import XttsAudioConfig
                torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
                logger.info("已添加安全全局变量")
            except Exception as e:
                logger.warning(f"添加安全全局变量失败: {e}")
            
            # viXTTS 需要从 Hugging Face 手动下载
            # 下载模型文件
            logger.info("从 Hugging Face 下载 viXTTS 模型...")
            
            try:
                # 下载配置文件
                config_path = hf_hub_download(
                    repo_id="capleaf/viXTTS",
                    filename="config.json"
                )
                
                # 下载模型文件
                model_path = hf_hub_download(
                    repo_id="capleaf/viXTTS",
                    filename="model.pth"
                )
                
                # 下载 vocab 文件
                vocab_path = hf_hub_download(
                    repo_id="capleaf/viXTTS",
                    filename="vocab.json"
                )
                
                logger.info(f"配置文件: {config_path}")
                logger.info(f"模型文件: {model_path}")
                logger.info(f"词汇文件: {vocab_path}")
                
                # 获取模型目录
                model_dir = os.path.dirname(config_path)
                
                # 使用本地路径加载模型（model_path 应该是目录）
                vixtts_model = TTS(
                    model_path=model_dir,  # 使用目录而不是文件
                    config_path=config_path,
                    vocoder_path=None,
                    vocoder_config_path=None,
                    progress_bar=False,
                    gpu=False
                )
                
                logger.info("✅ viXTTS 模型加载成功")
                
            except Exception as e:
                logger.error(f"从 Hugging Face 下载失败: {e}")
                logger.info("尝试使用标准 XTTS v2 模型作为备选...")
                
                # 回退到标准 XTTS v2
                vixtts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
                logger.warning("⚠️ 使用 XTTS v2 代替 viXTTS（不支持越南语）")
            
            # 检查支持的语言
            if hasattr(vixtts_model, 'languages'):
                logger.info(f"支持的语言: {vixtts_model.languages}")
            
        except Exception as e:
            logger.error(f"viXTTS 模型加载失败: {e}")
            raise
    return vixtts_model

# 全局变量：参考音频路径（用于语音克隆）
default_speaker_wav = None

def get_default_speaker_wav(language: str = "zh"):
    """获取默认参考音频（根据语言选择）"""
    global default_speaker_wav
    
    if default_speaker_wav is None:
        try:
            from huggingface_hub import hf_hub_download
            logger.info(f"下载默认参考音频，语言: {language}...")
            
            # viXTTS 需要参考音频，下载默认的
            default_speaker_wav = hf_hub_download(
                repo_id="capleaf/viXTTS",
                filename="vi_sample.wav"  # 使用越南语样本（viXTTS 的默认样本）
            )
            logger.info(f"✓ 参考音频: {default_speaker_wav}")
        except Exception as e:
            logger.error(f"下载参考音频失败: {e}")
            default_speaker_wav = None
    
    return default_speaker_wav

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

# ==================== TTS 服务（viXTTS）====================
async def text_to_speech_vixtts(text: str, language: str = "zh") -> bytes:
    """文字转语音 - 使用 pyttsx3（完全离线，快速）
    
    Args:
        text: 要合成的文本
        language: 语言代码 (zh=中文, en=英文, vi=越南语)
    """
    try:
        logger.info(f"开始合成语音 (pyttsx3): {text[:50]}..., 语言: {language}")
        
        import pyttsx3
        import concurrent.futures
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # 在线程池中运行 pyttsx3（它是同步的）
            def generate_speech():
                engine = pyttsx3.init()
                
                # 获取所有可用语音
                voices = engine.getProperty('voices')
                logger.info(f"系统可用语音数量: {len(voices)}")
                
                # 打印所有语音信息（调试用）
                for i, voice in enumerate(voices):
                    logger.info(f"语音 {i}: {voice.name} | ID: {voice.id} | Languages: {voice.languages}")
                
                # 选择中文语音
                chinese_voice = None
                if language == "zh":
                    # 尝试多种方式找到中文语音
                    for voice in voices:
                        voice_name_lower = voice.name.lower()
                        voice_id_lower = voice.id.lower()
                        
                        # 检查是否包含中文相关关键词
                        if any(keyword in voice_name_lower or keyword in voice_id_lower 
                               for keyword in ['chinese', 'mandarin', 'zh-cn', 'huihui', 'kangkang', 'yaoyao']):
                            chinese_voice = voice
                            logger.info(f"✓ 找到中文语音: {voice.name}")
                            break
                
                if chinese_voice:
                    engine.setProperty('voice', chinese_voice.id)
                else:
                    logger.warning("⚠️ 未找到中文语音，使用默认语音（可能是英文）")
                    logger.warning("建议安装 Windows 中文语音包")
                
                # 设置语速（默认 200，范围 0-400）
                engine.setProperty('rate', 200)
                
                # 设置音量（0.0-1.0）
                engine.setProperty('volume', 1.0)
                
                # 保存到文件
                engine.save_to_file(text, tmp_path)
                engine.runAndWait()
            
            # 在线程池中执行
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(generate_speech)
                future.result(timeout=30)  # 30秒超时
            
            # 读取生成的音频
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            logger.info(f"✅ 语音合成完成 (pyttsx3): {len(audio_data)} bytes")
            return audio_data
            
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                
    except Exception as e:
        logger.error(f"pyttsx3 失败: {str(e)}", exc_info=True)
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
    """流式对话接口（使用 requests 库避免 httpx 的 502 问题）"""
    try:
        logger.info(f"收到流式对话请求: {text[:50]}..., 语言: {language}")
        
        async def generate():
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    import requests
                    import concurrent.futures
                    
                    payload = {
                        "model": OLLAMA_MODEL,
                        "prompt": text,
                        "stream": False
                    }
                    
                    logger.info(f"发送请求到 Ollama (尝试 {attempt + 1}/{max_retries})...")
                    
                    # 在线程池中运行同步请求
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            requests.post,
                            f"{OLLAMA_HOST}/api/generate",
                            json=payload,
                            timeout=120
                        )
                        response = future.result()
                    
                    if response.status_code == 200:
                        data = response.json()
                        full_text = data.get("response", "")
                        
                        if full_text:
                            logger.info(f"收到响应，长度: {len(full_text)} 字符")
                            
                            # 立即开始生成语音（不等待文本发送完成）
                            logger.info(f"开始生成语音，语言: {language}...")
                            audio_task = asyncio.create_task(text_to_speech_vixtts(full_text, language))
                            
                            # 同时发送文本（更快的分块）
                            chunk_size = 20  # 增大分块大小
                            for i in range(0, len(full_text), chunk_size):
                                chunk = full_text[i:i+chunk_size]
                                yield f"data: {json.dumps({'text': chunk})}\n\n"
                                await asyncio.sleep(0.02)  # 减少延迟
                            
                            # 等待语音生成完成
                            audio_bytes = await audio_task
                            logger.info(f"语音完成，大小: {len(audio_bytes)} bytes")
                            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                            yield f"data: {json.dumps({'audio': audio_base64, 'done': True})}\n\n"
                        else:
                            yield f"data: {json.dumps({'error': 'Ollama 返回空响应'})}\n\n"
                    else:
                        raise Exception(f"HTTP {response.status_code}")
                    
                    break
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}, {retry_delay}秒后重试...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        logger.error(f"失败，已重试 {max_retries} 次: {str(e)}")
                        yield f"data: {json.dumps({'error': f'服务暂时不可用: {str(e)}'})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
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
        
        audio_bytes = await text_to_speech_vixtts(reply_text, language)
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
        "tts": f"viXTTS (supports Vietnamese)",
        "tts_model": VIXTTS_MODEL,
        "supported_languages": ["zh-cn", "en", "vi"],
        "mode": "完全离线 / Fully Offline"
    }

@app.on_event("startup")
async def startup_event():
    """启动时预加载模型"""
    logger.info("=" * 50)
    logger.info("AI 语音助手服务启动中（完全离线 - pyttsx3）...")
    logger.info(f"Ollama: {OLLAMA_HOST}")
    logger.info(f"模型: {OLLAMA_MODEL}")
    logger.info(f"Whisper: {WHISPER_MODEL}")
    logger.info(f"TTS 引擎: pyttsx3 (完全离线，快速)")
    logger.info("=" * 50)
    
    try:
        logger.info("预加载 Whisper 模型...")
        load_whisper()
        logger.info("✅ Whisper 模型加载完成")
    except Exception as e:
        logger.warning(f"预加载失败，将在首次请求时加载: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
