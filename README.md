# AI语音识别模板
## 仅保留主线预留接口、必要依赖、空资源目录和空测试模板

> ⚠️ 本项目仅限学术、研究、个人学习用途，禁止任何形式的商业使用（包括但不限于销售、SaaS、企业内部工具等）。如需商用请联系作者获得授权。

## 许可证与商用限制

本项目采用 CC BY-NC 4.0 非商业许可，详情见 LICENSE 文件。

---

## 项目简介

本项目为开源精简版，仅保留所有主要服务的预留接口，无任何实际模型或第三方 API 对接逻辑，适合二次开发或作为接口模板参考。

### 主要预留接口

- WebSocket 服务（Node.js，server.js）：仅返回占位消息，无实际业务逻辑
- ASR 服务（Python，paraformer_service.py）：仅返回占位文本，无语音识别模型
- LLM 服务（Python，llm_api.py）：仅返回占位回复，无大模型对接

---

## 目录结构

```
ai-open-source\
│
├── README.md                        # 本文档（项目总览）
├── LICENSE                          # CC BY-NC 4.0 非商业许可
├── .env.example                     # 环境变量示例
├── requirements.txt                 # Python依赖（仅 Flask/CORS）
├── package.json/package-lock.json    # Node依赖（仅 ws）
├── .gitignore                       # 忽略配置
│
├── websocket-demo/                  # 主服务目录
│   ├── Controller.html              # 前端页面（可自定义）
│   ├── server.js                    # WebSocket 预留服务
│   ├── paraformer_service.py        # ASR 预留服务
│   ├── llm_api.py                   # LLM 预留服务
│   ├── User.csv                     # 用户数据（演示用）
│   ├── funasr-runtime-resources/    # 资源目录（无模型权重）
│   └── tests/                       # 测试目录（可自定义）
│
└── .github/
    └── copilot-instructions.md      # 开源合规检查清单
```

---

## 快速启动（仅演示接口，无实际功能）

1. 安装依赖：
   - Python: `pip install flask flask-cors`
   - Node: `npm install`
2. 启动服务：
   - WebSocket：`node websocket-demo/server.js`
   - ASR：`python websocket-demo/paraformer_service.py`
   - LLM：`python websocket-demo/llm_api.py`

---

## 预留接口说明

### WebSocket 服务（server.js）

- 端口：8080
- 功能：所有连接仅收到占位消息 `{ type: 'info', message: '[此处为预留接口，未接入任何业务逻辑]' }`

### ASR 服务（paraformer_service.py）

- 端口：5000
- POST /asr：返回 `{ success: true, text: '[此处为预留接口，未接入任何模型]' }`
- GET /health：返回服务状态

### LLM 服务（llm_api.py）

- 端口：5001
- POST /llm：返回 `{ success: true, reply: '[此处为预留接口，未接入任何模型]' }`
- POST /llm/stream：SSE 流式返回占位内容
- POST /llm/clear：返回清空历史占位消息
- GET /health：返回服务状态

---

## 二次开发建议

- 可在各预留接口处集成实际模型、API 或业务逻辑
- 前端 Controller.html 可自定义为实际应用界面
- User.csv 仅为演示账号，生产环境请替换为安全认证方案
- funasr-runtime-resources/ 仅为资源目录，无模型权重

---

## 其他说明

- 本项目已彻底移除所有第三方模型、API 对接及相关依赖，仅保留接口模板
- 适合开源发布、教学演示或作为自定义语音/LLM 系统的起点
- 如需完整功能请参考历史版本或自行集成

---

**祝您使用愉快！** 🎉

如有问题请查阅本 README 或相关代码。
