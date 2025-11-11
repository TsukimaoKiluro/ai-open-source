#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR 服务预留接口，无实际模型接入
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/asr', methods=['POST'])
def asr_stub():
    return jsonify({"success": True, "text": "[此处为预留接口，未接入任何模型]"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "ASR Service (预留)"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
