#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paraformer 语音识别服务 (部署在 F 盘)
使用 ModelScope 的 Paraformer-large ONNX 在线流式模型
"""

from funasr import AutoModel
import os
import sys

def initialize_model():
    """初始化 Paraformer 模型"""
    print("=" * 70)
    print("正在加载 Paraformer Large ASR 模型...")
    print("模型: paraformer-zh (ONNX 优化版本)")
    print("=" * 70)
    
    try:
        # 加载 Paraformer 模型
        model = AutoModel(
            model="paraformer-zh",
            model_revision="v2.0.4",
            device="cpu",  # 使用 CPU，如果有 NVIDIA GPU 可以改为 "cuda"
        )
        print("\n✅ 模型加载成功！")
        print(f"📁 模型缓存位置: {os.path.expanduser('~/.cache/modelscope')}")
        return model
    except Exception as e:
        print(f"\n❌ 模型加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def transcribe_audio(model, audio_file):
    """
    转录音频文件
    
    Args:
        model: 已加载的模型
        audio_file: 音频文件路径 (支持 wav, mp3, m4a, flac 等格式)
    
    Returns:
        识别结果文本
    """
    try:
        print(f"\n{'='*70}")
        print(f"🎤 正在识别音频: {audio_file}")
        print(f"{'='*70}")
        
        # 执行识别
        result = model.generate(input=audio_file)
        
        if result and len(result) > 0:
            text = result[0]["text"]
            print(f"\n✅ 识别结果:")
            print(f"   {text}")
            print(f"\n{'='*70}")
            return text
        else:
            print("\n⚠️  未识别到内容")
            return ""
            
    except Exception as e:
        print(f"\n❌ 识别失败: {e}")
        import traceback
        traceback.print_exc()
        return ""

def test_model(model):
    """测试模型（使用示例音频）"""
    print("\n" + "="*70)
    print("📋 模型测试模式")
    print("="*70)
    
    # 检查是否有测试音频文件
    test_files = [
        "test.wav", "sample.wav", "test.mp3", 
        "recording.wav", "audio.wav", "demo.wav"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n✅ 找到测试文件: {test_file}")
            transcribe_audio(model, test_file)
            return
    
    print("\n⚠️  未找到测试音频文件。")
    print("\n📖 使用说明:")
    print("  1. 将音频文件（推荐 16kHz，WAV 格式）放在当前目录")
    print("  2. 运行: python paraformer_service.py <音频文件名>")
    print("\n💡 示例:")
    print("  python paraformer_service.py test.wav")
    print("  python paraformer_service.py recording.mp3")
    print("  python paraformer_service.py ../audio/sample.wav")

def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎙️  Paraformer 中文语音识别服务")
    print("="*70)
    print(f"📂 工作目录: {os.getcwd()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"💾 部署位置: F:\\桂林理工智能体项目\\paraformer-asr")
    
    # 初始化模型
    model = initialize_model()
    
    if model is None:
        print("\n❌ 模型初始化失败，程序退出")
        print("💡 提示: 请确保网络连接正常，模型会自动从 ModelScope 下载")
        sys.exit(1)
    
    # 如果提供了音频文件参数
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        if os.path.exists(audio_file):
            transcribe_audio(model, audio_file)
        else:
            print(f"\n❌ 文件不存在: {audio_file}")
            print(f"📂 当前目录: {os.getcwd()}")
            print(f"💡 请检查文件路径是否正确")
    else:
        # 测试模式
        test_model(model)
    
    print("\n" + "="*70)
    print("✅ 服务就绪！可以使用命令行进行语音识别")
    print("="*70)
    print("\n💡 提示:")
    print("  - 支持音频格式: WAV, MP3, M4A, FLAC 等")
    print("  - 最佳采样率: 16kHz")
    print("  - 支持中文普通话和方言识别")

if __name__ == "__main__":
    main()
