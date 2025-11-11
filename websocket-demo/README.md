# WebSocket 方言识别系统

基于 WebSocket 的实时通信系统，集成 Paraformer 中文方言识别功能。

## 📁 项目结构

```
websocket-demo/
├── server.js                    # Node.js WebSocket 服务器（已集成 Paraformer）
├── paraformer_api_server.py     # Python API 服务（Paraformer 模型）
├── Controller.html              # 控制端页面
├── login.html                   # 登录页面
├── User.csv                     # 用户数据
├── package.json                 # Node.js 依赖配置
├── start-server.bat             # 一键启动脚本（同时启动两个服务）
└── README.md                    # 本文档
```

## 🚀 快速开始

### 前置要求

1. **Node.js** （推荐 v18+）
2. **Python 3.11+** 虚拟环境（位于 `F:\桂林理工智能体项目\paraformer-asr\venv`）
3. **Python 依赖**：flask, flask-cors, funasr, torch, torchaudio
4. **FFmpeg**（强烈推荐，用于音频处理）- 详见 [FFmpeg 安装指南](FFMPEG_INSTALL.md)

> ⚠️ **重要**: 如果未安装 FFmpeg，系统会使用 torchaudio 作为备用方案，但功能可能受限。强烈建议安装 FFmpeg 以获得最佳性能。

### 安装步骤

#### 1. 安装 Python 依赖（如果尚未安装）

```powershell
# 创建虚拟环境
cd F:\桂林理工智能体项目\paraformer-asr
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install flask flask-cors funasr torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2. 安装 Node.js 依赖

```powershell
cd F:\桂林理工智能体项目\websocket-demo
npm install
```

#### 3. 安装 FFmpeg（强烈推荐）

**Windows - 使用 Chocolatey（推荐）：**

```powershell
choco install ffmpeg -y
```

**Windows - 使用 Scoop：**

```powershell
scoop install ffmpeg
```

**Windows - 手动安装：**

1. 下载: https://www.gyan.dev/ffmpeg/builds/
2. 解压到 `C:\ffmpeg\`
3. 添加 `C:\ffmpeg\bin` 到系统 PATH

**详细安装说明**: 请查看 [FFMPEG_INSTALL.md](FFMPEG_INSTALL.md)

> 💡 启动脚本会自动检测 ffmpeg 是否安装，如未安装会显示警告但不影响运行

### 启动应用

#### 方式一：一键启动（推荐）✨

双击 `start-server.bat` 或在命令行执行：

```cmd
cd F:\桂林理工智能体项目\websocket-demo
start-server.bat
```

脚本会自动：

1. ✅ 检查 Node.js 和 Python 环境
2. ✅ 安装缺失的依赖
3. ✅ 清理占用端口的旧进程
4. ✅ 启动 Paraformer API 服务（端口 5000，新窗口）
5. ✅ 等待模型加载并验证服务健康状态
6. ✅ 启动 WebSocket 服务（端口 8080）
7. ✅ 显示实时日志

**停止服务**: 按 `Ctrl+C`，脚本会自动清理所有进程

#### 方式二：使用管理脚本

我们提供了完整的服务管理脚本：

```cmd
# 启动服务
.\start-server.bat

# 停止服务（强制清理所有进程）
.\stop-server.bat

# 重启服务（先停止再启动）
.\restart-server.bat
```

**详细说明**: 请查看 [服务管理脚本说明.md](服务管理脚本说明.md)

#### 方式三：手动启动（用于调试）

**终端 1 - 启动 Python API 服务：**

```powershell
cd F:\桂林理工智能体项目\websocket-demo
F:\桂林理工智能体项目\paraformer-asr\venv\Scripts\python.exe paraformer_api_server.py
```

**终端 2 - 启动 Node.js 服务：**

```powershell
cd F:\桂林理工智能体项目\websocket-demo
node server.js
```

### 访问应用

启动成功后，在浏览器中访问：

- **登录页面**: http://localhost:8080
- **控制端**: http://localhost:8080/Controller.html
- **API 健康检查**: http://localhost:5000/health

默认用户账号（见 `User.csv`）：

- 用户名: `teacher` / 密码: `123456`
- 用户名: `student1` / 密码: `123456`

## 🎯 核心功能

### 1. AI 方言识别 🎙️

- ✅ **Paraformer 中文方言识别模型**

  - 基于阿里达摩院 Paraformer-zh v2.0.4
  - 支持多种中文方言识别
  - 高准确度和低延迟

- ✅ **多格式音频支持**

  - WebM, OGG, MP3, WAV, M4A 等
  - 自动格式检测和转换

- ✅ **实时语音转文字**
  - WebSocket 实时音频流传输
  - 端到端语音识别
  - 识别结果实时广播

### 2. 实时通信 💬

- ✅ WebSocket 双向通信
- ✅ 多用户连接支持
- ✅ 实时消息广播
- ✅ 用户身份认证

### 3. 音频流处理 🎵

- ✅ 分片音频传输
- ✅ 流式音频缓冲
- ✅ 自动格式识别
- ✅ Base64 编码支持

### 4. 智能语音端点检测 (VAD) 🎯

- ✅ **Silero VAD 端点检测**

  - 自动检测语音开始和结束
  - 中文语音优化参数
  - 智能过滤背景噪音

- ✅ **中文语音特性优化**

  - 适应中文声调变化（四声、轻声）
  - 容忍词间停顿（"嗯"、"呃"等）
  - 完整捕捉句首句尾音节
  - 支持不同语速和方言

- ✅ **双重检测机制**
  - Silero VAD（首选）- AI 模型检测
  - 基础音量检测（备用）- 音量阈值检测

> 💡 **VAD 参数已针对中文优化**: 详见 [VAD\_中文优化说明.md](VAD_中文优化说明.md)

## 📡 API 接口

### Paraformer API 端点

#### 1. 健康检查

```http
GET http://127.0.0.1:5000/health
```

**响应示例：**

```json
{
  "status": "ok",
  "model": "paraformer-zh",
  "version": "v2.0.4"
}
```

#### 2. 语音识别

```http
POST http://127.0.0.1:5000/transcribe
Content-Type: audio/webm

[音频二进制数据]
```

**响应示例：**

```json
{
  "success": true,
  "text": "识别的文本内容",
  "language": "zh",
  "confidence": 1.0
}
```

#### 3. 流式识别

```http
POST http://127.0.0.1:5000/transcribe-stream
Content-Type: application/json

{
  "audio": "base64_encoded_audio",
  "format": "webm",
  "streamId": "unique-id",
  "isLast": false
}
```

### WebSocket 消息格式

#### 客户端 → 服务器

**开始语音流：**

```json
{
  "type": "stream-start",
  "streamId": "unique-stream-id",
  "mimeType": "audio/webm",
  "username": "user123"
}
```

**发送音频分片：**

```json
{
  "type": "audio-chunk",
  "streamId": "unique-stream-id",
  "seq": 1,
  "mimeType": "audio/webm"
}
```

后跟二进制音频数据

**结束语音流：**

```json
{
  "type": "stream-end",
  "streamId": "unique-stream-id"
}
```

#### 服务器 → 客户端

**识别结果：**

```json
{
  "type": "stt-result",
  "sender": "user123",
  "streamId": "unique-stream-id",
  "result": {
    "type": "final",
    "text": "识别的文本内容"
  }
}
```

## 🔧 配置说明

### 服务器端口

- **WebSocket 服务**: 8080（可在 `server.js` 第 388 行修改）
- **Paraformer API**: 5000（可在 `server.js` 第 9 行和 `paraformer_api_server.py` 末尾修改）

### Python 虚拟环境路径

如果虚拟环境路径不同，请修改 `start-server.bat` 第 57 行：

```bat
set VENV_PATH=你的虚拟环境路径
```

### 模型配置

Paraformer 模型配置位于 `paraformer_api_server.py` 第 38-43 行：

```python
model = AutoModel(
    model="paraformer-zh",
    model_revision="v2.0.4",
    device="cpu",  # 改为 "cuda" 可使用 GPU 加速
    disable_update=True,
)
```

## 📝 使用说明

### 1. 登录系统

1. 打开 http://localhost:8080
2. 输入用户名和密码（见 `User.csv`）
3. 点击登录

### 2. 使用控制端

1. 登录后自动跳转到控制端
2. 点击"开始录音"按钮
3. 说话（支持各种方言）
4. 点击"停止录音"
5. 等待识别结果显示

### 3. 实时语音识别

- 录音时音频会实时传输到服务器
- Paraformer 模型会自动识别方言内容
- 识别结果会实时显示在页面上
- 所有连接的客户端都能看到识别结果

## 🛠️ 故障排除

### 问题 1: Paraformer API 服务无法启动

**错误信息**: `❌ 未找到 Python 虚拟环境`

**解决方案**:

```powershell
cd F:\桂林理工智能体项目\paraformer-asr
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install flask flask-cors funasr torch torchaudio
```

### 问题 2: 识别失败 "Paraformer API 服务不可用"

**可能原因**: Python API 服务未启动或端口被占用

**解决方案**:

1. 检查 Paraformer API 服务是否运行
2. 访问 http://localhost:5000/health 测试
3. 检查端口 5000 是否被占用：`netstat -ano | findstr :5000`

### 问题 3: npm install 失败

**解决方案**:

```powershell
# 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install
```

### 问题 4: 模型下载慢

**解决方案**:

模型会自动下载到 `~/.cache/modelscope/`，首次启动需要较长时间。可使用国内镜像加速：

```python
# 在 paraformer_api_server.py 中添加
os.environ['MODELSCOPE_CACHE'] = '自定义缓存路径'
```

### 问题 5: FFmpeg 未安装警告

**错误信息**: `⚠️ Notice: ffmpeg is not installed. torchaudio is used to load audio`

**影响**:

- 系统会使用 torchaudio 作为备用方案
- 某些音频格式可能不支持
- 处理性能可能较低

**解决方案**:

**Windows:**

```powershell
# 使用 Chocolatey（推荐）
choco install ffmpeg -y

# 或使用 Scoop
scoop install ffmpeg
```

**详细安装指南**: 查看 [FFMPEG_INSTALL.md](FFMPEG_INSTALL.md)

安装后重新运行 `start-server.bat` 即可，启动脚本会自动检测 ffmpeg。

### 问题 6: FFmpeg 已安装但仍提示未找到

**解决方案**:

1. 确认 ffmpeg 在系统 PATH 中：
   ```cmd
   ffmpeg -version
   ```
2. 如果提示找不到命令，重新添加到 PATH：
   - 找到 ffmpeg.exe 所在目录
   - 添加该目录到系统环境变量 PATH
   - **重启终端/命令行窗口**
3. 重新运行 `start-server.bat`

## 📚 技术栈

- **前端**: HTML5, JavaScript, WebSocket API, Web Audio API
- **后端**: Node.js, Express, WebSocket (ws)
- **AI 模型**: Paraformer-zh (阿里达摩院)
- **Python**: Flask, FunASR, PyTorch
- **数据格式**: JSON, CSV, Binary Audio

## 🔗 相关链接

- [Paraformer 模型](https://www.modelscope.cn/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch)
- [FunASR 文档](https://github.com/alibaba-damo-academy/FunASR)
- [WebSocket 协议](https://developer.mozilla.org/zh-CN/docs/Web/API/WebSocket)

## 📄 许可证

本项目仅供学习和研究使用。

## 🙋 支持

如有问题，请检查：

1. Python 虚拟环境是否正确配置
2. 所有依赖是否已安装
3. 端口 5000 和 8080 是否被占用
4. 模型文件是否下载完整

---

**开发团队**: 桂林理工大学智能体项目组  
**更新日期**: 2025 年 11 月 8 日
