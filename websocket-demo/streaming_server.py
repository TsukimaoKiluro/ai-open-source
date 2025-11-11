#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized WebSocket Streaming ASR Server
Based on reference code with improvements
"""

import asyncio
import websockets
import logging
import numpy as np
import torch
import json
import wave
import tempfile
import os
from funasr import AutoModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
asr_model = None
vad_model = None
vad_utils = None

# VAD configuration
VAD_CONFIG = {
    'threshold': 0.5,           # Speech probability threshold
    'begin_frames': 7,          # Frames to confirm speech start
    'end_frames': 25,           # Frames to confirm speech end
    'frame_size': 1024,         # Audio frame size in bytes
    'sample_rate': 16000,       # Sample rate
}


def int2float(sound):
    """Convert int16 audio to float32"""
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1 / 32768
    sound = sound.squeeze()
    return sound


def load_vad_model():
    """Load Silero VAD model"""
    global vad_model, vad_utils
    try:
        torch.set_num_threads(1)
        vad_model, vad_utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        logger.info("Silero VAD model loaded successfully")
        return True
    except Exception as e:
        logger.warning(f"Failed to load VAD model: {e}")
        logger.info("Continuing without server-side VAD")
        return False


def load_asr_model(model_name='paraformer-zh'):
    """Load ASR model"""
    global asr_model
    try:
        logger.info(f"Loading ASR model: {model_name}")
        
        if model_name == 'paraformer-large':
            # Try local path first
            local_path = '../models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
            if os.path.exists(local_path):
                asr_model = AutoModel(
                    model=local_path,
                    device="cpu",
                    disable_update=True,
                )
            else:
                asr_model = AutoModel(
                    model='iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
                    model_revision='master',
                    device="cpu",
                    disable_update=True,
                )
        else:
            # Default paraformer-zh
            asr_model = AutoModel(
                model='paraformer-zh',
                model_revision='v2.0.4',
                device="cpu",
                disable_update=True,
            )
        
        logger.info("ASR model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load ASR model: {e}")
        return False


async def process_audio_with_vad(audio_data):
    """Process audio chunk with VAD"""
    if not vad_model or len(audio_data) < VAD_CONFIG['frame_size']:
        return None
    
    try:
        audio_int16 = np.frombuffer(audio_data[:VAD_CONFIG['frame_size']], np.int16)
        audio_float32 = int2float(audio_int16)
        
        with torch.no_grad():
            speech_prob = vad_model(
                torch.from_numpy(audio_float32), 
                VAD_CONFIG['sample_rate']
            ).item()
        
        return speech_prob
    except Exception as e:
        logger.error(f"VAD processing error: {e}")
        return None


async def recognize_audio(audio_data):
    """Perform ASR on audio data"""
    if not asr_model or len(audio_data) < 1000:
        return ""
    
    try:
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Write WAV file
            with wave.open(tmp_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(VAD_CONFIG['sample_rate'])
                wav_file.writeframes(audio_array.tobytes())
        
        # Perform recognition
        result = asr_model.generate(input=tmp_path, batch_size=1)
        
        # Clean up
        os.unlink(tmp_path)
        
        if result and len(result) > 0:
            text = result[0].get('text', '')
            logger.info(f"Recognition result: {text}")
            return text
        
        return ""
        
    except Exception as e:
        logger.error(f"Recognition error: {e}")
        return ""


async def handle_streaming_client(websocket, path):
    """Handle streaming audio from client with VAD"""
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(f"Client connected: {client_id}")
    
    # State machine
    state = 0  # 0: waiting for speech, 1: in speech
    begin_count = 0
    end_count = 0
    
    # Audio buffers
    audio_buffer = b''
    speech_buffer = b''
    
    try:
        async for message in websocket:
            # Handle binary audio data
            if isinstance(message, bytes):
                audio_buffer += message
                
                # Process when we have enough data
                while len(audio_buffer) >= VAD_CONFIG['frame_size']:
                    frame = audio_buffer[:VAD_CONFIG['frame_size']]
                    audio_buffer = audio_buffer[VAD_CONFIG['frame_size']:]
                    
                    # Perform VAD
                    speech_prob = await process_audio_with_vad(frame)
                    
                    if speech_prob is None:
                        # No VAD available, accumulate and send back empty
                        speech_buffer += frame
                        await websocket.send(json.dumps({
                            'type': 'vad_status',
                            'probability': 0
                        }))
                        continue
                    
                    # State machine logic
                    if state == 0:  # Waiting for speech
                        if speech_prob > VAD_CONFIG['threshold']:
                            begin_count += 1
                            speech_buffer += frame
                            
                            if begin_count >= VAD_CONFIG['begin_frames']:
                                # Speech started
                                state = 1
                                begin_count = 0
                                logger.info(f"Speech started (client: {client_id})")
                                await websocket.send(json.dumps({
                                    'type': 'speech_start'
                                }))
                        else:
                            begin_count = 0
                            speech_buffer = b''
                    
                    elif state == 1:  # In speech
                        speech_buffer += frame
                        
                        if speech_prob < VAD_CONFIG['threshold']:
                            end_count += 1
                            
                            if end_count >= VAD_CONFIG['end_frames']:
                                # Speech ended
                                state = 0
                                end_count = 0
                                logger.info(f"Speech ended, recognizing... (client: {client_id})")
                                
                                # Perform recognition
                                text = await recognize_audio(speech_buffer)
                                
                                # Send result
                                await websocket.send(json.dumps({
                                    'type': 'recognition_result',
                                    'text': text,
                                    'audio_length': len(speech_buffer)
                                }))
                                
                                # Reset buffer
                                speech_buffer = b''
                        else:
                            end_count = 0
                    
                    # Send VAD status
                    await websocket.send(json.dumps({
                        'type': 'vad_status',
                        'probability': speech_prob,
                        'state': 'speech' if state == 1 else 'silence'
                    }))
            
            # Handle JSON control messages
            elif isinstance(message, str):
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'reset':
                        # Reset state
                        state = 0
                        begin_count = 0
                        end_count = 0
                        audio_buffer = b''
                        speech_buffer = b''
                        logger.info(f"Client reset: {client_id}")
                        
                    elif msg_type == 'config':
                        # Update configuration
                        if 'threshold' in data:
                            VAD_CONFIG['threshold'] = data['threshold']
                        logger.info(f"Config updated: {client_id}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {client_id}")
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error handling client {client_id}: {e}")


async def main():
    """Main server function"""
    logger.info("="*70)
    logger.info("Streaming ASR Server Starting...")
    logger.info("="*70)
    
    # Load VAD model (optional)
    vad_loaded = load_vad_model()
    if not vad_loaded:
        logger.warning("Server-side VAD not available, relying on client-side VAD")
    
    # Load ASR model
    if not load_asr_model():
        logger.error("Failed to load ASR model, exiting")
        return
    
    # Start WebSocket server
    host = "0.0.0.0"
    port = 10096
    
    logger.info("="*70)
    logger.info(f"Server listening on ws://{host}:{port}")
    logger.info("Ready to accept connections")
    logger.info("="*70)
    
    async with websockets.serve(
        handle_streaming_client,
        host,
        port,
        ping_interval=20,
        ping_timeout=10
    ):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
