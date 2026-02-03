"""
AI Voice Service - gTTS 版本（支持越南语）
使用 Google Text-to-Speech 支持越南语
需要网络连接
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
# Dify 工作流配置（中文/英文）
DIFY_API_URL = "http://10.0.0.10:3099/v1/chat/completions"
DIFY_API_KEY = "http://10.0.0.10:180/v1|app-bzBAseue8wuzdhSCG8O05fkI|Chat"
DIFY_MODEL = "dify"

# Ollama 配置（越南语 + 备用）
OLLAMA_HOST = "http://10.0.0.10:11434"
OLLAMA_MODEL = "qwen2.5:7b"

SERVICE_PORT = 8001

# Whisper 模型大小
WHISPER_MODEL = "small"

# TTS 引擎：使用 gTTS（支持越南语，需要网络）
TTS_ENGINE = "gtts"

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI Voice Service - gTTS (Vietnamese Support)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全局变量（延迟加载）====================
whisper_model = None

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

# ==================== TTS 服务（gTTS）====================
async def text_to_speech_gtts(text: str, language: str = "zh") -> bytes:
    """文字转语音 - 使用 gTTS（支持越南语，需要网络）
    
    Args:
        text: 要合成的文本
        language: 语言代码 (zh=中文, en=英文, vi=越南语)
    """
    try:
        logger.info(f"开始合成语音 (gTTS): {text[:50]}..., 语言: {language}")
        
        from gtts import gTTS
        import subprocess
        
        # gTTS 语言代码映射
        lang_map = {
            "zh": "zh-CN",  # 中文（简体）
            "en": "en",     # 英文
            "vi": "vi"      # 越南语
        }
        
        gtts_lang = lang_map.get(language, "en")
        logger.info(f"使用 gTTS 语言: {gtts_lang}")
        
        # 生成语音
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        
        # 保存到临时 MP3 文件
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
            mp3_path = tmp_mp3.name
        
        try:
            tts.save(mp3_path)
            logger.info(f"gTTS 生成 MP3: {mp3_path}")
            
            # 转换 MP3 到 WAV（更好的兼容性）
            wav_path = mp3_path.replace(".mp3", ".wav")
            
            # 使用 ffmpeg 转换
            if os.path.exists(FFMPEG_EXE):
                ffmpeg_cmd = FFMPEG_EXE
            else:
                ffmpeg_cmd = "ffmpeg"
            
            cmd = [
                ffmpeg_cmd,
                "-i", mp3_path,
                "-acodec", "pcm_s16le",
                "-ar", "22050",
                "-ac", "1",
                "-y",
                wav_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            if result.returncode == 0:
                # 读取 WAV 文件
                with open(wav_path, 'rb') as f:
                    audio_data = f.read()
                logger.info(f"✅ 语音合成完成 (gTTS): {len(audio_data)} bytes")
                os.unlink(wav_path)
            else:
                # 如果转换失败，直接返回 MP3
                logger.warning("WAV 转换失败，返回 MP3")
                with open(mp3_path, 'rb') as f:
                    audio_data = f.read()
            
            return audio_data
            
        finally:
            if os.path.exists(mp3_path):
                try:
                    os.unlink(mp3_path)
                except:
                    pass
                
    except Exception as e:
        logger.error(f"gTTS 失败: {str(e)}", exc_info=True)
        # 返回空音频
        logger.warning("TTS 失败，返回空音频")
        return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'

# ==================== Dify 工作流 LLM ====================
async def chat_with_dify(text: str, user_name: str = "用户", language: str = "zh") -> str:
    """与 Dify 工作流对话（非流式）"""
    # 越南语优先使用 Ollama，如果失败则尝试 Dify
    if language == "vi":
        logger.info("检测到越南语，优先使用 Ollama 服务")
        try:
            return await chat_with_ollama_fallback(text, language)
        except Exception as e:
            logger.warning(f"Ollama 失败: {e}，尝试使用 Dify（可能不支持越南语）")
            # 继续执行 Dify 调用
    
    try:
        logger.info(f"发送到 Dify 工作流: {text[:50]}... (语言: {language})")
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": DIFY_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": f"用户名：{user_name}"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7,
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DIFY_API_KEY}"
            }
            
            response = await client.post(DIFY_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not reply:
                logger.warning("Dify 返回空响应，尝试使用备用 Ollama")
                return await chat_with_ollama_fallback(text, language)
            
            logger.info(f"Dify 回复: {reply[:50]}...")
            return reply
            
    except Exception as e:
        logger.error(f"Dify 工作流失败: {str(e)}")
        logger.info("尝试使用备用 Ollama 服务...")
        try:
            return await chat_with_ollama_fallback(text, language)
        except:
            raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")

async def chat_with_ollama_fallback(text: str, language: str = "zh") -> str:
    """备用 Ollama 对话"""
    try:
        logger.info(f"发送到 Ollama (备用/越南语): {text[:50]}... (语言: {language})")
        
        language_prompts = {
            "zh": "请用中文回答：",
            "en": "Please answer in English: ",
            "vi": "Vui lòng trả lời bằng tiếng Việt: "
        }
        prompt_prefix = language_prompts.get(language, "")
        full_prompt = f"{prompt_prefix}{text}" if prompt_prefix else text
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False
            }
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            reply = result.get("response", "")
            logger.info(f"Ollama 回复: {reply[:50]}...")
            return reply
    except httpx.ConnectError as e:
        logger.error(f"Ollama 连接失败: {OLLAMA_HOST} - {str(e)}")
        raise Exception(f"无法连接到 Ollama 服务 ({OLLAMA_HOST})")
    except httpx.TimeoutException as e:
        logger.error(f"Ollama 超时: {str(e)}")
        raise Exception("Ollama 服务响应超时")
    except Exception as e:
        logger.error(f"Ollama 服务失败: {str(e)}")
        raise Exception(f"Ollama 服务错误: {str(e)}")

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

@app.post("/chat")
async def chat(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    language: str = Form("zh"),
    user_name: str = Form("用户")
):
    """统一聊天接口（使用 gTTS）"""
    try:
        logger.info(f"收到请求 - text: {text}, audio: {audio is not None}, language: {language}, user: {user_name}")
        
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
        
        reply_text = await chat_with_dify(input_text, user_name, language)
        
        audio_bytes = await text_to_speech_gtts(reply_text, language)
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
        "llm_service": "Dify Workflow (中文/英文) + Ollama (越南语)",
        "dify_api": DIFY_API_URL,
        "ollama_host": OLLAMA_HOST,
        "whisper_model": WHISPER_MODEL,
        "asr": "openai-whisper (local)",
        "tts": "gTTS (Google Text-to-Speech, 需要网络)",
        "tts_support": "完美支持中文、英文、越南语",
        "supported_languages": ["zh-cn", "en", "vi"],
        "mode": "智能语言路由 + gTTS 语音",
        "routing": {
            "zh": "Dify Workflow",
            "en": "Dify Workflow",
            "vi": "Ollama (Dify 不支持越南语)"
        },
        "note": "gTTS 需要网络连接"
    }

@app.on_event("startup")
async def startup_event():
    """启动时预加载模型"""
    logger.info("=" * 50)
    logger.info("AI 语音助手服务启动中（gTTS 版本）...")
    logger.info(f"LLM 服务: Dify Workflow + Ollama")
    logger.info(f"Whisper: {WHISPER_MODEL}")
    logger.info(f"TTS 引擎: gTTS (Google Text-to-Speech)")
    logger.info(f"越南语支持: ✅ 完美支持（通过 gTTS）")
    logger.info("=" * 50)
    
    try:
        logger.info("预加载 Whisper 模型...")
        load_whisper()
        logger.info("✅ Whisper 模型加载完成")
    except Exception as e:
        logger.warning(f"预加载失败，将在首次请求时加载: {e}")
    
    # 测试 gTTS
    try:
        from gtts import gTTS
        logger.info("✅ gTTS 可用")
    except ImportError:
        logger.error("❌ gTTS 未安装！请运行: pip install gtts")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
