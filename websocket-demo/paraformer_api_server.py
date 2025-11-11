#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paraformer  HTTP API 
 HTTP  Node.js WebSocket 
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from funasr import AutoModel
import tempfile
import os
import sys
import traceback
import logging
import subprocess
import shutil

app = Flask(__name__)
CORS(app)

# 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
models = {}  # Store multiple models
current_model_name = 'paraformer-zh'  # Default model
ffmpeg_available = False

# Available models configuration
AVAILABLE_MODELS = {
    'paraformer-zh': {
        'name': 'Paraformer-zh (Default)',
        'model_id': 'paraformer-zh',
        'revision': 'v2.0.4',
        'description': 'Standard Chinese ASR model'
    },
    'paraformer-large': {
        'name': 'Paraformer-zh Large',
        'model_id': 'iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
        'revision': 'master',
        'description': 'Large Chinese ASR model with better accuracy',
        'local_path': '../models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
    }
}

def check_ffmpeg():
    """ ffmpeg """
    global ffmpeg_available
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            ffmpeg_available = True
            logger.info(" ffmpeg ")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    #  Scoop 
    scoop_ffmpeg = os.path.expanduser("~/scoop/shims/ffmpeg.exe")
    if os.path.exists(scoop_ffmpeg):
        try:
            result = subprocess.run([scoop_ffmpeg, '-version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                ffmpeg_available = True
                logger.info(f" ffmpeg  (Scoop): {scoop_ffmpeg}")
                return True
        except:
            pass
    
    logger.warning("  ffmpeg ")
    ffmpeg_available = False
    return False

def convert_audio_to_wav(input_path, output_path, sample_rate=16000):
    """Use ffmpeg to convert audio to WAV format with specified sample rate"""
    try:
        # Check input file
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return False
        
        input_size = os.path.getsize(input_path)
        if input_size < 100:
            logger.error(f"Input file too small: {input_size} bytes")
            return False
        
        logger.info(f"Input file: {input_path} ({input_size} bytes)")
        
        ffmpeg_cmd = 'ffmpeg'
        scoop_ffmpeg = os.path.expanduser("~/scoop/shims/ffmpeg.exe")
        if os.path.exists(scoop_ffmpeg):
            ffmpeg_cmd = scoop_ffmpeg
        
        cmd = [
            ffmpeg_cmd,
            '-loglevel', 'warning',
            '-i', input_path,
            '-ar', str(sample_rate),  # Sample rate: 8000 or 16000
            '-ac', '1',               # Mono
            '-acodec', 'pcm_s16le',   # PCM 16-bit
            '-f', 'wav',
            '-avoid_negative_ts', 'make_zero',
            '-y',
            output_path
        ]
        
        logger.info(f"Converting to {sample_rate}Hz WAV...")
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0:
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                logger.info(f"Conversion success: {output_path} ({output_size} bytes, {sample_rate}Hz)")
                return True
            else:
                logger.error(f"Output file not created: {output_path}")
                return False
        else:
            logger.error(f"FFmpeg conversion failed (exit code {result.returncode})")
            if result.stderr:
                logger.error(f"stderr: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg timeout (>30s)")
        return False
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        traceback.print_exc()
        return False

def initialize_model(model_name='paraformer-zh'):
    """Initialize Paraformer model"""
    global models, current_model_name
    
    if model_name in models:
        logger.info(f"Model '{model_name}' already loaded")
        current_model_name = model_name
        return True
    
    logger.info("="*70)
    logger.info(f"Initializing model: {model_name}...")
    logger.info("="*70)
    
    # Check ffmpeg
    check_ffmpeg()
    
    try:
        model_config = AVAILABLE_MODELS.get(model_name)
        if not model_config:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        # Check if local model exists
        local_path = model_config.get('local_path')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if local_path:
            full_local_path = os.path.join(script_dir, local_path)
            if os.path.exists(full_local_path):
                logger.info(f"Loading local model from: {full_local_path}")
                loaded_model = AutoModel(
                    model=full_local_path,
                    device="cpu",
                    disable_update=True,
                )
            else:
                logger.info(f"Local model not found, downloading from ModelScope...")
                loaded_model = AutoModel(
                    model=model_config['model_id'],
                    model_revision=model_config.get('revision', 'master'),
                    device="cpu",
                    disable_update=True,
                )
        else:
            # Load from ModelScope
            loaded_model = AutoModel(
                model=model_config['model_id'],
                model_revision=model_config.get('revision', 'v2.0.4'),
                device="cpu",
                disable_update=True,
            )
        
        models[model_name] = loaded_model
        current_model_name = model_name
        logger.info(f"Model '{model_name}' loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        traceback.print_exc()
        return False

def get_current_model():
    """Get current active model"""
    return models.get(current_model_name)
    logger.info("="*70)
    
    #  ffmpeg
    check_ffmpeg()
    
    try:
        #  Paraformer 
        model = AutoModel(
            model="paraformer-zh",
            model_revision="v2.0.4",
            device="cpu",  #  CPU GPU  "cuda"
            disable_update=True,  # 
        )
        logger.info(" ")
        logger.info(f" : {os.path.expanduser('~/.cache/modelscope')}")
        return True
    except Exception as e:
        logger.error(f" : {e}")
        traceback.print_exc()
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    model = get_current_model()
    if model is None:
        return jsonify({
            'status': 'error',
            'message': 'Model not initialized'
        }), 503
    return jsonify({
        'status': 'ok',
        'model': current_model_name,
        'available_models': list(AVAILABLE_MODELS.keys()),
        'ffmpeg': 'available' if ffmpeg_available else 'not_found'
    })

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({
        'current': current_model_name,
        'loaded': list(models.keys()),
        'available': {k: v['name'] for k, v in AVAILABLE_MODELS.items()}
    })

@app.route('/switch_model', methods=['POST'])
def switch_model():
    """Switch to a different model"""
    data = request.get_json()
    model_name = data.get('model', 'paraformer-zh')
    
    if model_name not in AVAILABLE_MODELS:
        return jsonify({
            'success': False,
            'error': f'Unknown model: {model_name}',
            'available': list(AVAILABLE_MODELS.keys())
        }), 400
    
    if initialize_model(model_name):
        return jsonify({
            'success': True,
            'model': model_name,
            'message': f'Switched to {model_name}'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to load model'
        }), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    
    
     base64
    
    
    - Content-Type: audio/* ()
    - Content-Type: application/json (JSON: { "audio": "base64_data", "format": "webm" })
    
    
    {
        "success": true,
        "text": "",
        "language": "zh"
    }
    """
    model = get_current_model()
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not initialized'
        }), 503
    
    try:
        audio_data = None
        file_ext = ".wav"
        
        # 
        if request.content_type and 'audio' in request.content_type:
            # 
            audio_data = request.data
            
            #  Content-Type 
            if 'webm' in request.content_type:
                file_ext = ".webm"
            elif 'ogg' in request.content_type:
                file_ext = ".ogg"
            elif 'mp4' in request.content_type or 'm4a' in request.content_type:
                file_ext = ".m4a"
            elif 'mpeg' in request.content_type or 'mp3' in request.content_type:
                file_ext = ".mp3"
                
        elif request.is_json:
            # JSON base64 
            data = request.get_json()
            import base64
            audio_data = base64.b64decode(data.get('audio', ''))
            file_ext = "." + data.get('format', 'wav')
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported content type'
            }), 400
        
        if not audio_data:
            return jsonify({
                'success': False,
                'error': 'No audio data received'
            }), 400
        
        # 
        if len(audio_data) < 100:
            logger.warning(f" : {len(audio_data)} ")
            return jsonify({
                'success': True,
                'text': '',
                'language': 'zh',
                'confidence': 0.0,
                'message': ''
            })
        
        logger.info(f" : {len(audio_data)} , : {file_ext}")
        
        # 
        if len(audio_data) > 16:
            header_hex = audio_data[:16].hex()
            logger.info(f"  (16): {header_hex}")
            
            # 
            if len(audio_data) > 64:
                header_64 = audio_data[:64].hex()
                logger.info(f"  (64): {header_64}")
        
        #  WebM 
        if file_ext == '.webm':
            # WebM  0x1A 0x45 0xDF 0xA3 EBML 
            if len(audio_data) > 4:
                header = audio_data[:4]
                expected_header = b'\x1a\x45\xdf\xa3'
                
                if header != expected_header:
                    logger.warning(f" WebM ")
                    logger.warning(f"   : {expected_header.hex()}")
                    logger.warning(f"   : {header.hex()}")
                    
                    #  2KB  WebM EBML 
                    search_length = min(len(audio_data), 2048)
                    webm_pos = audio_data[:search_length].find(b'\x1a\x45\xdf\xa3')
                    
                    if webm_pos > 0:
                        logger.info(f"  {webm_pos}  WebM ")
                        audio_data = audio_data[webm_pos:]
                        logger.info(f"   : {len(audio_data)} ")
                    elif webm_pos < 0:
                        #  WebM 
                        logger.warning("  WebM EBML ")
                        logger.warning("    MediaRecorder ")
                        logger.warning("   ")
                        
                        # 
                        if audio_data[:4] == b'RIFF':
                            logger.info("    RIFF  WAV ")
                            file_ext = '.wav'
                        elif audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
                            logger.info("    MP3 ")
                            file_ext = '.mp3'
                else:
                    logger.info(f" WebM EBML ")
        
        # 
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_data)
            temp_file.flush()  # 
        
        try:
            logger.info(f" : {temp_path} ({len(audio_data)} )")
            
            # Convert to WAV if needed
            final_audio_path = temp_path
            converted = False
            
            if file_ext.lower() != '.wav' and ffmpeg_available:
                logger.info(f"Converting {file_ext} to WAV format...")
                
                # Try 16kHz first (preferred for Paraformer)
                wav_path_16k = temp_path.replace(file_ext, '_16k.wav')
                success_16k = convert_audio_to_wav(temp_path, wav_path_16k, sample_rate=16000)
                
                if success_16k and os.path.exists(wav_path_16k):
                    output_size = os.path.getsize(wav_path_16k)
                    logger.info(f"16kHz conversion output: {output_size} bytes")
                    
                    if output_size > 100:
                        final_audio_path = wav_path_16k
                        converted = True
                        logger.info(f"Using 16kHz WAV file")
                    else:
                        logger.warning(f"16kHz WAV too small ({output_size} bytes), trying 8kHz...")
                        # Try 8kHz as fallback
                        wav_path_8k = temp_path.replace(file_ext, '_8k.wav')
                        success_8k = convert_audio_to_wav(temp_path, wav_path_8k, sample_rate=8000)
                        
                        if success_8k and os.path.exists(wav_path_8k):
                            output_size_8k = os.path.getsize(wav_path_8k)
                            if output_size_8k > 100:
                                final_audio_path = wav_path_8k
                                converted = True
                                logger.info(f"Using 8kHz WAV file ({output_size_8k} bytes)")
                            else:
                                logger.warning(f"Both conversions failed, trying original file")
                        else:
                            logger.warning(f"8kHz conversion also failed, trying original file")
                else:
                    logger.warning(f"FFmpeg 16kHz conversion failed, trying 8kHz...")
                    wav_path_8k = temp_path.replace(file_ext, '_8k.wav')
                    success_8k = convert_audio_to_wav(temp_path, wav_path_8k, sample_rate=8000)
                    
                    if success_8k and os.path.exists(wav_path_8k):
                        output_size_8k = os.path.getsize(wav_path_8k)
                        if output_size_8k > 100:
                            final_audio_path = wav_path_8k
                            converted = True
                            logger.info(f"Using 8kHz WAV file ({output_size_8k} bytes)")
                        else:
                            logger.warning(f"All conversions failed, trying original file")
                    else:
                        logger.warning(f"All conversions failed, trying original file")
                        
            elif file_ext.lower() != '.wav' and not ffmpeg_available:
                logger.warning("ffmpeg not available, trying to use original non-WAV file")
            
            # Perform recognition
            logger.info(f"Starting recognition: {final_audio_path}")
            logger.info(f"  File exists: {os.path.exists(final_audio_path)}")
            logger.info(f"  File size: {os.path.getsize(final_audio_path)} bytes")
            
            try:
                result = model.generate(input=final_audio_path)
                
                if not result or len(result) == 0:
                    logger.warning(" ")
                    return jsonify({
                        'success': True,
                        'text': '',
                        'language': 'zh',
                        'confidence': 0.0,
                        'message': ''
                    })
                    
            except Exception as model_error:
                logger.error(f" : {model_error}")
                logger.error(f"   : {type(model_error).__name__}")
                traceback.print_exc()
                
                error_msg = str(model_error)
                error_lower = error_msg.lower()
                
                # 
                if 'format' in error_lower or 'codec' in error_lower or 'decode' in error_lower:
                    return jsonify({
                        'success': False,
                        'error': '',
                        'detail': error_msg,
                        'suggestion': ''
                    }), 500
                elif 'sample' in error_lower or 'rate' in error_lower:
                    return jsonify({
                        'success': False,
                        'error': '',
                        'detail': error_msg,
                        'suggestion': ' 16kHz'
                    }), 500
                elif 'channel' in error_lower:
                    return jsonify({
                        'success': False,
                        'error': '',
                        'detail': error_msg,
                        'suggestion': ''
                    }), 500
                else:
                    # 
                    return jsonify({
                        'success': False,
                        'error': '',
                        'detail': error_msg,
                        'suggestion': ''
                    }), 500
            
            # Clean up converted temporary files
            if converted:
                # Clean up both 16k and 8k versions if they exist
                for suffix in ['_16k.wav', '_8k.wav', '.wav']:
                    temp_wav = temp_path.replace(file_ext, suffix)
                    if temp_wav != temp_path and os.path.exists(temp_wav):
                        try:
                            os.unlink(temp_wav)
                            logger.info(f"Cleaned up: {temp_wav}")
                        except:
                            pass
                try:
                    os.unlink(final_audio_path)
                except:
                    pass
            
            if result and len(result) > 0:
                text = result[0].get("text", "")
                logger.info(f" : {text}")
                
                return jsonify({
                    'success': True,
                    'text': text,
                    'language': 'zh',
                    'confidence': 1.0
                })
            else:
                logger.warning(" ")
                return jsonify({
                    'success': True,
                    'text': '',
                    'language': 'zh',
                    'confidence': 0.0
                })
        finally:
            # 
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f" : {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/transcribe-stream', methods=['POST'])
def transcribe_stream():
    """
    
    
    JSON
    {
        "audio": "base64_encoded_audio_chunk",
        "format": "webm",
        "streamId": "unique-stream-id",
        "isLast": false
    }
    
    
    {
        "success": true,
        "text": "",
        "isFinal": false
    }
    """
    model = get_current_model()
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not initialized'
        }), 503
    
    try:
        data = request.get_json()
        stream_id = data.get('streamId', 'unknown')
        is_last = data.get('isLast', False)
        
        import base64
        audio_data = base64.b64decode(data.get('audio', ''))
        file_ext = "." + data.get('format', 'webm')
        
        if not audio_data:
            return jsonify({
                'success': False,
                'error': 'No audio data'
            }), 400
        
        # 
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_data)
        
        try:
            # 
            result = model.generate(input=temp_path)
            
            text = ""
            if result and len(result) > 0:
                text = result[0].get("text", "")
            
            logger.info(f"  [{stream_id}] isFinal={is_last}: {text}")
            
            return jsonify({
                'success': True,
                'text': text,
                'isFinal': is_last,
                'streamId': stream_id
            })
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f" : {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def main():
    """"""
    print("\n" + "="*70)
    print("  Paraformer  API ")
    print("="*70)
    print(f" Python: {sys.version.split()[0]}")
    print(f" : {os.getcwd()}")
    print("="*70)
    
    # 
    if not initialize_model():
        print("\n ")
        sys.exit(1)
    
    print("\n" + "="*70)
    print(" API ")
    print("="*70)
    print("\n API :")
    print("  - GET  /health           : ")
    print("  - POST /transcribe       : ")
    print("  - POST /transcribe-stream: ")
    print("\n : http://0.0.0.0:5000")
    print("="*70 + "\n")
    
    #  Flask 
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)

if __name__ == "__main__":
    main()
