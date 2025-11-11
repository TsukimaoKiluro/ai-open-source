# 🎙️ 桂林理工方言识别系统 - 使用指南

> **⚠️ 重要更新：** 现已支持两套系统！
>
> 1. **原系统（聊天室模式）** - 位于 `websocket-demo/`
> 2. **FunASR WSS（2-Pass 实时流式）** - 新增专业语音识别服务
>
> 详见：[系统架构对比.md](../系统架构对比.md) | [FunASR WSS 部署指南](../FUNASR_WSS_部署指南.md)

## ✅ 系统已部署完成

**⚠️ 注意**: 项目实际位置已更改！

**正确的项目位置**: `F:\桂林理工智能体项目\websocket-demo\`

所有文件已整合到此目录，包括：

- ✅ WebSocket 服务器 (server.js) - 已集成 Paraformer API
- ✅ Paraformer API 服务 (paraformer_service.py)
- ✅ 前端页面 (Controller.html, login.html) - 中文 VAD 优化
- ✅ 用户数据 (User.csv)
- ✅ 启动脚本 (start-server.bat)
- ✅ Node.js 依赖已安装（包括 axios）
- ✅ Python 依赖已安装（包括 funasr）
- ✅ Paraformer 模型已下载
- ✅ **FFmpeg 已集成** - 支持多种音频格式转换

---

## 🚀 启动系统

### ⚠️ 重要：使用正确的目录

**正确路径**: `F:\桂林理工智能体项目\websocket-demo\`

### 方法一：批处理一键启动（推荐）

```cmd
cd F:\桂林理工智能体项目\websocket-demo
start-server.bat
```

这将自动：

1. 检查 Node.js 和 FFmpeg 环境
2. 启动 Paraformer API 服务（新窗口，端口 5000）
3. 启动 WebSocket 服务器（当前窗口，端口 8080）
4. 显示浏览器访问地址
5. 实时输出日志

### 方法二：手动启动（用于调试）

**终端 1 - 启动 Python API:**

```powershell
cd F:\桂林理工智能体项目\websocket-demo
F:\桂林理工智能体项目\paraformer-asr\venv\Scripts\python.exe paraformer_service.py
```

**终端 2 - 启动 WebSocket 服务器:**

```powershell
cd F:\桂林理工智能体项目\websocket-demo
node server.js
```

---

## 🌐 访问系统

启动成功后：

1. **登录页面**: http://localhost:8080
2. **控制端**: http://localhost:8080/Controller.html
3. **API 测试**: http://localhost:5000/health

---

## 👤 登录账号

编辑 `User.csv` 查看可用账号：

```csv
username,password
admin,123456
test,test123
```

---

## 🎤 使用步骤

### 1. 登录系统

- 打开浏览器访问 http://localhost:8080
- 输入用户名和密码（例如：admin / 123456）
- 点击「登录」

### 2. 选择麦克风

- 进入控制端后，点击「选择麦克风」按钮
- 从下拉列表中选择您的麦克风设备
- 点击「确认」

### 3. 开启语音识别

- 点击「开启语音检测」按钮
- 浏览器会请求麦克风权限，点击「允许」
- 按钮变为「关闭语音检测」，表示已启用

### 4. 开始说话

- 对着麦克风说话（普通话或方言）
- VAD 会自动检测到语音并开始录音
- 音频实时发送到服务器

### 5. 查看识别结果

- 说话结束后（静音 0.5 秒）会自动停止录音
- 音频发送到 Paraformer 模型进行识别
- 识别结果显示在聊天区域
- 格式：`[STT] 您的用户名: 识别的文本内容`

### 6. 停止识别

- 点击「关闭语音检测」停止语音识别
- 麦克风会释放

---

## 🔍 功能说明

### VAD (Voice Activity Detection) - 已针对中文优化 ✨

- **Silero VAD**: 智能语音端点检测
- **自动触发**: 检测到说话自动开始录音
- **自动结束**: 静音超过 0.5 秒自动停止
- **中文优化参数**:
  - 开始说话阈值: 0.6（降低以适应中文声调）
  - 停止说话阈值: 0.35（降低以减少误截断）
  - 救赎帧数: 16（增加以允许停顿）
  - 前置填充: 3 帧（保留句首）
  - 最小语音帧: 5 帧（过滤短噪音）

### 音频参数

- **录音格式**: WebM (Opus 编码)
- **支持格式**: WebM, OGG, WAV, MP3（自动转换）
- **采样率**: 48kHz → 自动转换为 16kHz
- **声道**: 自动转换为单声道
- **分片间隔**: 250ms per chunk
- **传输协议**: WebSocket 二进制流
- **格式转换**: FFmpeg 自动处理

### 识别能力

- **模型**: Paraformer Large (944MB)
- **语言**: 中文普通话 + 方言
- **延迟**: 1-3 秒（取决于音频长度）
- **准确率**: 高精度（工业级）

---

## 📊 系统监控

### 查看 Python API 状态

```powershell
# 方法 1: 浏览器访问
http://localhost:5000/health

# 方法 2: PowerShell
Invoke-RestMethod -Uri http://localhost:5000/health

# 预期输出:
# {
#   "status": "ok",
#   "model": "paraformer-zh",
#   "version": "v2.0.4",
#   "ffmpeg": "available"
# }
```

### 查看 WebSocket 连接

打开浏览器开发者工具（F12）：

- **Network** 标签 → **WS** → 查看 WebSocket 连接
- **Console** 标签 → 查看音频流和识别结果日志

### 查看服务日志

- **Python API**: 查看 Python 终端窗口，显示每次识别请求
- **WebSocket**: 查看 Node.js 终端窗口，显示连接和消息

---

## 🐛 常见问题

### Q1: FFmpeg 未找到警告

**解决方法**:

```powershell
# 使用 Scoop 安装（推荐）
scoop install ffmpeg

# 或使用 Chocolatey
choco install ffmpeg

# 安装后重启服务
```

### Q2: 识别失败：服务器错误（可能是音频格式问题）

**原因**: 这是我们已经修复的问题！
**解决**:

1. 确保 FFmpeg 已安装（参考 Q1）
2. 确保使用的是最新版本的 `paraformer_service.py`
3. 系统会自动将 WebM/OGG 转换为 WAV
4. 查看 API 日志中的转换信息

### Q3: 启动脚本报错找不到 Python

**解决方法**:

```powershell
# 检查虚拟环境
Test-Path "F:\桂林理工智能体项目\paraformer-asr\venv\Scripts\python.exe"

# 如果返回 False，重新创建虚拟环境
cd F:\桂林理工智能体项目\paraformer-asr
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install flask flask-cors funasr torch torchaudio
```

### Q4: Node.js 报错找不到模块

**解决方法**:

```powershell
cd F:\桂林理工智能体项目\websocket-demo
npm install
```

### Q5: 识别结果显示错误信息

**可能原因**:

1. **Python API 未启动**: 先启动 `paraformer_service.py`
2. **端口被占用**: 关闭其他占用 5000 端口的程序
3. **防火墙阻止**: 允许 Python 和 Node.js 通过防火墙
4. **音频格式不支持**: 确保 FFmpeg 已安装

**检查方法**:

```powershell
# 检查端口占用
netstat -ano | findstr "5000"
netstat -ano | findstr "8080"
```

### Q6: 麦克风权限被拒绝

**解决方法**:

1. 浏览器地址栏左侧点击「锁」图标
2. 找到「麦克风」权限设置
3. 选择「允许」
4. 刷新页面

### Q7: VAD 库加载失败

**解决方法**:

- 确保网络连接正常（需要从 unpkg CDN 加载）
- 使用 Chrome/Edge 最新版浏览器
- 检查浏览器控制台是否有 CORS 错误

### Q8: 识别结果为空或乱码

**可能原因**:

1. **音频太短**: 至少说 1 秒以上
2. **音量太小**: 调整麦克风音量
3. **背景噪音**: 在安静环境测试
4. **音频格式**: 确保浏览器支持 WebM 格式

---

## 🔧 高级配置

### 使用 GPU 加速（如果有 NVIDIA 显卡）

编辑 `paraformer_api_server.py` 第 31 行：

```python
device="cuda"  # 从 "cpu" 改为 "cuda"
```

需要安装 CUDA 和 cuDNN，并确保 `onnxruntime-gpu` 已安装。

### 修改端口

**Python API 端口（默认 5000）**:
编辑 `paraformer_api_server.py` 最后一行：

```python
app.run(host='127.0.0.1', port=5000, ...)
```

**WebSocket 端口（默认 8080）**:
编辑 `server.js` 最后几行：

```javascript
const PORT = 8080;
```

### 调整 VAD 灵敏度

编辑 `Controller.html`，搜索 `positiveSpeechThreshold`:

```javascript
positiveSpeechThreshold: 0.8,  // 降低此值更容易触发（0.5-0.95）
negativeSpeechThreshold: 0.75, // 降低此值更快停止（0.35-0.8）
```

---

## 📦 文件结构

```
F:\桂林理工智能体项目\websocket-demo\  ← 正确的项目目录
│
├── 📄 paraformer_service.py     ← Python API 服务（含 FFmpeg 集成）
├── 📄 server.js                 ← WebSocket 服务器（含 API 对接）
├── 📄 Controller.html           ← 控制端页面（中文 VAD 优化）
├── 📄 login.html                ← 登录页面
├── 📄 User.csv                  ← 用户数据
│
├── 📄 package.json              ← Node.js 配置（含 axios）
├── 📁 node_modules/             ← Node.js 依赖
│
├── 🚀 start-server.bat          ← 统一启动脚本
│
├── 📖 README.md                 ← 完整项目说明
├── 📖 FFMPEG_INSTALL.md         ← FFmpeg 安装指南
├── 📖 VAD_中文优化说明.md       ← VAD 参数详解
├── 📖 500错误排查指南.md        ← 错误处理指南
└── 📖 音频格式问题修复总结.md   ← 最新修复说明
```

---

## 📞 获取帮助

### 查看详细文档

- **项目说明**: `README.md`
- **部署配置**: `DEPLOYMENT.md`
- **使用指南**: `USAGE.md`（本文件）

### 运行测试

```cmd
cd F:\桂林理工智能体项目\dialect-recognition-app
test.bat
```

### 检查服务状态

```powershell
# WebSocket 服务
curl http://localhost:8080

# Python API 服务
curl http://localhost:5000/health
```

---

## 🎯 下一步

系统已完全部署并可以使用！

**建议测试流程**:

1. ✅ 运行 `start.ps1` 启动服务
2. ✅ 访问 http://localhost:8080 登录
3. ✅ 选择麦克风设备
4. ✅ 开启语音检测
5. ✅ 对着麦克风说「你好，测试一下方言识别」
6. ✅ 查看识别结果

**成功标志**:

- 聊天区域显示：`[STT] 您的用户名: 你好测试一下方言识别`

---

**项目完成日期**: 2025 年 11 月 8 日  
**部署位置**: F:\桂林理工智能体项目\dialect-recognition-app\
