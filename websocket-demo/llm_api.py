#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API 预留接口服务
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LLM_PORT = int(os.getenv("LLM_PORT", "5001"))

@app.route('/llm', methods=['POST'])
def llm_chat():
    """
    预留 LLM 对话接口（非流式）
    """
    # 仅返回占位响应
    return jsonify({"success": True, "reply": "[此处为预留接口，未接入任何模型]"})  # noqa: E501


@app.route('/llm/stream', methods=['POST'])
def llm_chat_stream():
    """
    预留 LLM 对话接口（流式）
    """
    def generate():
        yield "data: [此处为预留接口，未接入任何模型]\n\n"
        yield "data: [DONE]\n\n"
    return Response(generate(), mimetype='text/event-stream')


@app.route('/llm/clear', methods=['POST'])
def clear_history():
    """
    预留清空对话历史接口
    """
    return jsonify({"success": True, "message": "[预留接口，无历史可清空]"})


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({"status": "ok", "service": "LLM API Service (预留)", "model": "none"})


if __name__ == '__main__':
    logger.info("启动 LLM API 预留服务...")
    logger.info(f"API 地址: http://localhost:{LLM_PORT}")
    app.run(host='0.0.0.0', port=LLM_PORT, debug=False)
