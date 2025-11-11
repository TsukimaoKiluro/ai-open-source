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

# 
model = None
ffmpeg_available = False

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

def convert_audio_to_wav(input_path, output_path):
    """ ffmpeg  WAV """
    try:
        # 
        if not os.path.exists(input_path):
            logger.error(f" : {input_path}")
            return False
        
        input_size = os.path.getsize(input_path)
        if input_size < 100:
            logger.error(f" : {input_size} ")
            return False
        
        logger.info(f" : {input_path} ({input_size} )")
        
        ffmpeg_cmd = 'ffmpeg'
        scoop_ffmpeg = os.path.expanduser("~/scoop/shims/ffmpeg.exe")
        if os.path.exists(scoop_ffmpeg):
            ffmpeg_cmd = scoop_ffmpeg
            logger.info(f"  Scoop ffmpeg: {scoop_ffmpeg}")
        
        cmd = [
            ffmpeg_cmd,
            '-loglevel', 'warning',  # 
            '-i', input_path,
            '-ar', '16000',          #  16kHz
            '-ac', '1',              # 
            '-acodec', 'pcm_s16le',  # PCM 
            '-f', 'wav',             #  WAV 
            '-avoid_negative_ts', 'make_zero',  # 
            '-y',                    # 
            output_path
        ]
        
        logger.info(f"  ffmpeg ...")
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0:
            # 
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                logger.info(f" : {output_path} ({output_size} )")
                return True
            else:
                logger.error(f" : {output_path}")
                return False
        else:
            logger.error(f" ffmpeg  ( {result.returncode})")
            logger.error(f"stderr: {result.stderr}")
            if result.stdout:
                logger.error(f"stdout: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f" ffmpeg >30")
        return False
    except Exception as e:
        logger.error(f" : {e}")
        traceback.print_exc()
        return False

def initialize_model():
    """ Paraformer """
    global model
    logger.info("="*70)
    logger.info(" Paraformer ...")
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
    """"""
    if model is None:
        return jsonify({
            'status': 'error',
            'message': 'Model not initialized'
        }), 503
    return jsonify({
        'status': 'ok',
        'model': 'paraformer-zh',
        'version': 'v2.0.4',
        'ffmpeg': 'available' if ffmpeg_available else 'not_found'
    })

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
            
            #  WAV  ffmpeg 
            final_audio_path = temp_path
            converted = False
            
            if file_ext.lower() != '.wav' and ffmpeg_available:
                logger.info(f"  {file_ext}  WAV ...")
                wav_path = temp_path.replace(file_ext, '.wav')
                
                # 
                input_size = os.path.getsize(temp_path)
                logger.info(f"   : {input_size} ")
                
                if convert_audio_to_wav(temp_path, wav_path):
                    # 
                    if os.path.exists(wav_path):
                        output_size = os.path.getsize(wav_path)
                        logger.info(f"   : {output_size} ")
                        
                        if output_size > 100:
                            final_audio_path = wav_path
                            converted = True
                            logger.info(f"  WAV ")
                        else:
                            logger.error(f"  WAV  ({output_size} )")
                            # 
                            logger.info(f" ")
                    else:
                        logger.error(f" : {wav_path}")
                        # 
                        logger.info(f" ")
                else:
                    logger.warning(f" FFmpeg ")
                    # 
            elif file_ext.lower() != '.wav' and not ffmpeg_available:
                logger.warning("  ffmpeg WAV ")
                # 
            
            # 
            logger.info(f" : {final_audio_path}")
            logger.info(f"   : {os.path.exists(final_audio_path)}")
            logger.info(f"   : {os.path.getsize(final_audio_path)} ")
            
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
            
            # 
            if converted and os.path.exists(final_audio_path):
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
    print("\n : http://127.0.0.1:5000")
    print("="*70 + "\n")
    
    #  Flask 
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)

if __name__ == "__main__":
    main()
