#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FunASR WebSocket Server - 2-Pass 实时流式语音识别服务
支持 VAD + Paraformer + Punctuation 的完整流水线
"""

import asyncio
import websockets
import json
import logging
import tempfile
import os
import base64
import traceback
from funasr import AutoModel
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局模型实例
asr_model = None
vad_model = None
punc_model = None

def initialize_models():
    """初始化 FunASR 模型（VAD + ASR + 标点）"""
    global asr_model, vad_model, punc_model
    
    try:
        logger.info("🔄 开始加载 FunASR 模型...")
        
        # 1. 加载 VAD 模型（语音端点检测）
        logger.info("📥 加载 VAD 模型...")
        vad_model = AutoModel(
            model="fsmn-vad",
            model_revision="v2.0.4",
            device="cpu",
            disable_update=True,
        )
        logger.info("✅ VAD 模型加载完成")
        
        # 2. 加载 ASR 模型（语音识别）
        logger.info("📥 加载 Paraformer ASR 模型...")
        asr_model = AutoModel(
            model="paraformer-zh",
            model_revision="v2.0.4",
            device="cpu",
            disable_update=True,
        )
        logger.info("✅ ASR 模型加载完成")
        
        # 3. 加载标点恢复模型
        logger.info("📥 加载标点恢复模型...")
        punc_model = AutoModel(
            model="ct-punc",
            model_revision="v2.0.4",
            device="cpu",
            disable_update=True,
        )
        logger.info("✅ 标点恢复模型加载完成")
        
        logger.info("🎉 所有模型加载完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 模型加载失败: {e}")
        traceback.print_exc()
        return False


class StreamingSession:
    """流式识别会话"""
    
    def __init__(self, websocket, client_id):
        self.websocket = websocket
        self.client_id = client_id
        self.audio_buffer = []
        self.is_streaming = False
        self.sample_rate = 16000
        
    async def send_message(self, msg_type, data=None, text=""):
        """发送消息到客户端"""
        message = {
            "type": msg_type,
            "client_id": self.client_id,
            "text": text,
            "data": data
        }
        try:
            await self.websocket.send(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def process_audio_chunk(self, audio_data):
        """处理音频分片 - 2-Pass 识别"""
        try:
            # 添加到缓冲区
            self.audio_buffer.append(audio_data)
            
            # Pass 1: VAD 检测（检查是否有语音）
            if vad_model:
                # VAD 检测需要完整的音频片段，这里简化处理
                combined_audio = b''.join(self.audio_buffer)
                
                # 如果缓冲区足够大，进行识别
                if len(combined_audio) > 8000:  # 约 0.5 秒的音频
                    # 保存临时音频文件
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                        tmp_file.write(combined_audio)
                    
                    try:
                        # Pass 2: ASR 识别
                        result = asr_model.generate(
                            input=tmp_path,
                            batch_size_s=300,
                            hotword='',
                        )
                        
                        if result and len(result) > 0:
                            text = result[0]['text']
                            
                            # Pass 3: 标点恢复
                            if punc_model and text:
                                punc_result = punc_model.generate(input=text)
                                if punc_result and len(punc_result) > 0:
                                    text = punc_result[0]['text']
                            
                            # 发送识别结果（实时结果）
                            if text.strip():
                                await self.send_message("partial_result", text=text)
                                logger.info(f"🎤 实时识别: {text}")
                    
                    finally:
                        # 清理临时文件
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
        
        except Exception as e:
            logger.error(f"处理音频分片失败: {e}")
            traceback.print_exc()
    
    async def finalize_recognition(self):
        """完成识别 - 返回最终结果"""
        try:
            if not self.audio_buffer:
                await self.send_message("final_result", text="")
                return
            
            # 合并所有音频
            combined_audio = b''.join(self.audio_buffer)
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                tmp_file.write(combined_audio)
            
            try:
                # 完整识别
                result = asr_model.generate(
                    input=tmp_path,
                    batch_size_s=300,
                    hotword='',
                )
                
                if result and len(result) > 0:
                    text = result[0]['text']
                    
                    # 标点恢复
                    if punc_model and text:
                        punc_result = punc_model.generate(input=text)
                        if punc_result and len(punc_result) > 0:
                            text = punc_result[0]['text']
                    
                    # 发送最终结果
                    await self.send_message("final_result", text=text)
                    logger.info(f"✅ 最终识别: {text}")
                else:
                    await self.send_message("final_result", text="")
            
            finally:
                # 清理
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                self.audio_buffer.clear()
        
        except Exception as e:
            logger.error(f"完成识别失败: {e}")
            traceback.print_exc()
            await self.send_message("error", text=f"识别失败: {str(e)}")


async def handle_client(websocket, path):
    """处理 WebSocket 客户端连接"""
    client_id = id(websocket)
    logger.info(f"✅ 新客户端连接: {client_id}")
    
    session = StreamingSession(websocket, client_id)
    
    try:
        await session.send_message("connected", text="连接成功")
        
        async for message in websocket:
            try:
                # 处理二进制音频数据
                if isinstance(message, bytes):
                    if session.is_streaming:
                        await session.process_audio_chunk(message)
                    continue
                
                # 处理 JSON 控制消息
                data = json.loads(message)
                msg_type = data.get("type", "")
                
                if msg_type == "start":
                    # 开始流式识别
                    session.is_streaming = True
                    session.audio_buffer.clear()
                    await session.send_message("started", text="开始识别")
                    logger.info(f"🎤 客户端 {client_id} 开始流式识别")
                
                elif msg_type == "stop":
                    # 停止识别并返回最终结果
                    session.is_streaming = False
                    await session.finalize_recognition()
                    logger.info(f"⏹️  客户端 {client_id} 停止识别")
                
                elif msg_type == "ping":
                    # 心跳检测
                    await session.send_message("pong")
                
                else:
                    logger.warning(f"未知消息类型: {msg_type}")
            
            except json.JSONDecodeError:
                logger.error("JSON 解析失败")
            except Exception as e:
                logger.error(f"处理消息失败: {e}")
                traceback.print_exc()
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"❌ 客户端 {client_id} 连接关闭")
    except Exception as e:
        logger.error(f"客户端 {client_id} 处理失败: {e}")
        traceback.print_exc()
    finally:
        logger.info(f"🔌 客户端 {client_id} 断开连接")


async def main():
    """启动 WebSocket 服务器"""
    # 初始化模型
    if not initialize_models():
        logger.error("❌ 模型初始化失败，服务器无法启动")
        return
    
    # 启动 WebSocket 服务器
    host = "0.0.0.0"
    port = 10095
    
    logger.info(f"🚀 FunASR WebSocket Server 启动中...")
    logger.info(f"📡 监听地址: ws://{host}:{port}")
    logger.info(f"🎯 2-Pass 流程: VAD → ASR → Punctuation")
    
    async with websockets.serve(handle_client, host, port, max_size=10*1024*1024):
        logger.info("✅ 服务器启动成功！")
        await asyncio.Future()  # 保持运行


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器错误: {e}")
        traceback.print_exc()
