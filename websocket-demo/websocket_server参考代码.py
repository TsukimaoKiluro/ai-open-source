# server.py
asr_model = None

import asyncio
import websockets
import logging
import numpy as np
import torch
import requests
import base64
import json
import wave


torch.set_num_threads(1)

vad_model, utils = torch.hub.load(
    source='local',
    repo_or_dir='/root/.cache/torch/hub/snakers4_silero-vad_master',
    # repo_or_dir='C:/Users/shiyu/.cache/torch/hub/snakers4_silero-vad_master',
    model='silero_vad',
    force_reload=False,
    onnx=False)

logging.basicConfig(level=logging.INFO)


def write_binary_audio_to_wav(audio_data, sample_rate, num_channels):
    """
    将二进制音频数据写入WAV文件

    参数:
    audio_data (bytes): 二进制音频数据
    sample_rate (int): 音频采样率
    num_channels (int): 音频通道数
    """
    # 将二进制数据转换为numpy数组
    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    # 创建WAV文件
    with wave.open("output.wav", "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(2)  # 每个样本占用2个字节
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_array.tobytes())

    print("音频已成功写入 output.wav 文件")


def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        # sound *= 1/16384
        sound *= 1 / 32768
    sound = sound.squeeze()  # depends on the use case
    return sound


async def asr(chunk):
    sample_offset = 0
    chunk_size = [0, 10, 5]  # [5, 10, 5] 600ms, [8, 8, 4] 480ms
    encoder_chunk_look_back = 4
    decoder_chunk_look_back = 1
    stride_size = chunk_size[1] * 960
    audio = np.frombuffer(chunk, np.int16)
    speech_length = audio.shape[0]
    cache = {}
    is_final = False
    try:
        for sample_offset in range(0, speech_length, min(stride_size, speech_length - sample_offset)):
            if sample_offset + stride_size >= speech_length - 1:
                stride_size = speech_length - sample_offset
                is_final = True
                print(stride_size)

            res = asr_model(audio[sample_offset: sample_offset + stride_size], cache=cache, is_final=is_final,
                                     encoder_chunk_look_back=encoder_chunk_look_back,
                                     decoder_chunk_look_back=decoder_chunk_look_back)
            if len(res[0]["value"]):
                print(res)
        return "asr_result"
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return ""
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return ""


async def handle_audio_stream(websocket):
    threshold = 0.8
    begin_max = 7  #
    end_max = 25
    send_vad_time_max = 3
    begin = 0
    end = 0
    send_vad_time = 0
    state = 0
    vad_state = False
    audio = b''
    data = b''
    try:
        logging.info("New client connected")
        while True:
            # 接收音频数据
            audio_chunk = await websocket.recv()

            audio += audio_chunk
            data += audio_chunk

            if len(audio) > 1024:
                new_data = audio[:1024]
                audio = audio[1024:]
                audio_int16 = np.frombuffer(new_data, np.int16)
                audio_float32 = int2float(audio_int16)
                with torch.no_grad():
                    speech_prob = vad_model(torch.from_numpy(audio_float32), 16000).item()
                # print(speech_prob)

                if speech_prob < threshold and state == 0:
                    begin = begin + 1

                if speech_prob < threshold and state == 1:
                    end = end + 1

                if speech_prob > threshold:
                    begin = 0
                    end = 0
                    state = 1

                if begin == begin_max:
                    begin = 0
                    data = b''
                    state = 0

                if end == end_max:
                    result = await asr(data)
                    # 进行语音识别

                    # 将识别结果发送回客户端
                    await websocket.send(result)
                    logging.info(f"Sent result: {result}")
                    end = 0
                    data = b''
                    state = 0
            # print(audio_chunk)
                else:
                    await websocket.send("")
            else:
                await websocket.send("")
            # print(audio_chunk)

            # audio += audio_chunk
            # print(len(audio))
            # data += audio_chunk

            # if len(audio) > 1024:
            #     new_data = audio[:1024]
            #     audio = audio[1024:]




    except websockets.ConnectionClosed:
        logging.info("Client disconnected")
    except Exception as e:
        logging.error(f"Error: {str(e)}")


async def main():
    global asr_model
    from modelscope.pipelines import pipeline
    from modelscope.utils.constant import Tasks
    asr_model = pipeline(
        task=Tasks.auto_speech_recognition,
        model='iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online',
        model_revision='v2.0.4',
    )
    server = await websockets.serve(
        handle_audio_stream,
        "10.203.7.85",
        8765,
        ping_interval=None
    )
    logging.info("WebSocket server started on ws://10.203.7.85:8765")
    await server.wait_closed()


if __name__ == "__main__":
    # print(asr_model_dir)
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
    # asyncio.run(main())