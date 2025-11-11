#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FunASR WebSocket Server - 2-Pass 实时流式语音识别
支持方言识别的 WebSocket 服务

作者: 桂林理工方言识别项目组
日期: 2025-11-08
"""

import asyncio
import websockets
import json
import logging
import io
import tempfile
import os
from pathlib import Path
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局模型实例
asr_model = None
punc_model = None


def initialize_models():
    """初始化 FunASR 模型"""
    global asr_model, punc_model
    
    logger.info("正在加载 Paraformer 流式模型...")
    try:
        # 使用 Paraformer-zh 流式模型
        asr_model = AutoModel(
            model="paraformer-zh-streaming",
            model_revision="v2.0.4",
            device="cpu",  # 如果有 GPU，改为 "cuda"
        )
        logger.info(" Paraformer 流式模型加载成功")
        
        # 加载标点模型（可选）
        try:
            punc_model = AutoModel(
                model="ct-punc",
                model_revision="v2.0.4", 
                device="cpu"
            )
            logger.info(" 标点模型加载成功")
        except Exception as e:
            logger.warning(f"️ 标点模型加载失败（可选功能）: {e}")
            punc_model = None
            
    except Exception as e:
        logger.error(f" 模型加载失败: {e}")
        raise


class AudioStreamHandler:
    """音频流处理器 - 处理实时音频流"""
    
    def __init__(self, websocket):
        self.websocket = websocket
        self.audio_buffer = bytearray()
        self.stream_id = None
        self.sample_rate = 16000
        self.is_streaming = False
        
    async def handle_message(self, message):
        """处理客户端消息"""
        try:
            if isinstance(message, bytes):
                # 二进制音频数据
                await self.handle_audio_chunk(message)
            else:
                # JSON 控制消息
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'start':
                    await self.handle_start(data)
                elif msg_type == 'end':
                    await self.handle_end(data)
                elif msg_type == 'ping':
                    await self.send_message({'type': 'pong'})
                else:
                    logger.warning(f"未知消息类型: {msg_type}")
                    
        except Exception as e:
            logger.error(f"处理消息错误: {e}", exc_info=True)
            await self.send_error(str(e))
    
    async def handle_start(self, data):
        """处理开始消息"""
        self.stream_id = data.get('streamId', 'unknown')
        self.sample_rate = data.get('sampleRate', 16000)
        self.audio_buffer.clear()
        self.is_streaming = True
        
        logger.info(f"️ 开始音频流: {self.stream_id}")
        await self.send_message({
            'type': 'started',
            'streamId': self.stream_id
        })
    
    async def handle_audio_chunk(self, audio_data):
        """处理音频块"""
        if not self.is_streaming:
            logger.warning("收到音频数据但流未启动")
            return
            
        self.audio_buffer.extend(audio_data)
        
        # 每收集到一定量的数据就进行一次识别（实时流式）
        if len(self.audio_buffer) >= 32000:  # 约 1 秒的数据 (16000*2字节)
            await self.process_audio_chunk()
    
    async def process_audio_chunk(self):
        """处理音频块并返回中间结果"""
        if not self.audio_buffer or not asr_model:
            return
            
        try:
            # 将音频数据保存为临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                
                # 写入 WAV 头
                import wave
                with wave.open(tmp_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(bytes(self.audio_buffer))
            
            # 使用 FunASR 进行流式识别
            result = asr_model.generate(
                input=tmp_path,
                batch_size=1,
                is_final=False  # 中间结果
            )
            
            # 清理临时文件
            os.unlink(tmp_path)
            
            if result and len(result) > 0:
                text = result[0].get('text', '')
                if text:
                    # 发送中间识别结果
                    await self.send_message({
                        'type': 'partial',
                        'streamId': self.stream_id,
                        'text': text,
                        'isFinal': False
                    })
                    logger.info(f" 中间结果: {text}")
            
            # 保留部分数据用于上下文连续性
            self.audio_buffer = self.audio_buffer[-16000:]  # 保留 0.5 秒
            
        except Exception as e:
            logger.error(f"处理音频块错误: {e}", exc_info=True)
    
    async def handle_end(self, data):
        """处理结束消息 - 最终识别"""
        if not self.is_streaming:
            return
            
        logger.info(f" 结束音频流: {self.stream_id}")
        self.is_streaming = False
        
        try:
            if len(self.audio_buffer) > 0 and asr_model:
                # 最终识别
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                    
                    import wave
                    with wave.open(tmp_path, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(self.sample_rate)
                        wav_file.writeframes(bytes(self.audio_buffer))
                
                # 最终识别
                result = asr_model.generate(
                    input=tmp_path,
                    batch_size=1,
                    is_final=True  # 最终结果
                )
                
                os.unlink(tmp_path)
                
                if result and len(result) > 0:
                    text = result[0].get('text', '')
                    
                    # 如果有标点模型，添加标点
                    if punc_model and text:
                        try:
                            punc_result = punc_model.generate(input=text)
                            if punc_result and len(punc_result) > 0:
                                text = punc_result[0].get('text', text)
                        except Exception as e:
                            logger.warning(f"标点处理失败: {e}")
                    
                    # 发送最终结果
                    await self.send_message({
                        'type': 'result',
                        'streamId': self.stream_id,
                        'text': text,
                        'isFinal': True
                    })
                    logger.info(f" 最终结果: {text}")
                else:
                    await self.send_message({
                        'type': 'result',
                        'streamId': self.stream_id,
                        'text': '',
                        'isFinal': True
                    })
            else:
                await self.send_message({
                    'type': 'result',
                    'streamId': self.stream_id,
                    'text': '',
                    'isFinal': True
                })
                
        except Exception as e:
            logger.error(f"最终识别错误: {e}", exc_info=True)
            await self.send_error(str(e))
        finally:
            self.audio_buffer.clear()
    
    async def send_message(self, data):
        """发送 JSON 消息"""
        try:
            await self.websocket.send(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.error(f"发送消息错误: {e}")
    
    async def send_error(self, error_msg):
        """发送错误消息"""
        await self.send_message({
            'type': 'error',
            'streamId': self.stream_id,
            'error': error_msg
        })


async def handle_client(websocket, path):
    """处理 WebSocket 客户端连接"""
    client_address = websocket.remote_address
    logger.info(f" 新客户端连接: {client_address}")
    
    handler = AudioStreamHandler(websocket)
    
    try:
        async for message in websocket:
            await handler.handle_message(message)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f" 客户端断开: {client_address}")
    except Exception as e:
        logger.error(f"处理客户端错误: {e}", exc_info=True)
    finally:
        logger.info(f" 清理连接: {client_address}")


async def main():
    """主函数"""
    # 初始化模型
    initialize_models()
    
    # 启动 WebSocket 服务器
    host = "0.0.0.0"
    port = 10095
    
    logger.info(f" FunASR WSS Server 启动中...")
    logger.info(f" 监听地址: ws://{host}:{port}")
    logger.info(f" 模型: Paraformer-zh-streaming v2.0.4")
    logger.info(f" 支持 2-Pass 实时流式识别")
    logger.info(f"=" * 60)
    
    async with websockets.serve(handle_client, host, port, ping_interval=20, ping_timeout=10):
        logger.info(" 服务器运行中，按 Ctrl+C 停止")
        await asyncio.Future()  # 运行直到被中断


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n 服务器已停止")
    except Exception as e:
        logger.error(f" 服务器错误: {e}", exc_info=True)
