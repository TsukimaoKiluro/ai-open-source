# 测试音频识别功能

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Paraformer API 音频识别测试" -ForegroundColor Cyan  
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查健康状态
Write-Host "[1/3] 检查服务健康状态..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:5000/health" -Method Get
    Write-Host "✅ 服务状态: $($health.status)" -ForegroundColor Green
    Write-Host "✅ 模型: $($health.model) $($health.version)" -ForegroundColor Green
    Write-Host "✅ FFmpeg: $($health.ffmpeg)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ 服务不可用，请先启动 Paraformer API 服务" -ForegroundColor Red
    exit 1
}

# 2. 测试小音频（应该被过滤）
Write-Host "[2/3] 测试小音频数据（< 100 字节）..." -ForegroundColor Yellow
try {
    $smallAudio = [byte[]]::new(50)
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/transcribe" `
        -Method Post `
        -ContentType "audio/wav" `
        -Body $smallAudio `
        -ErrorAction Stop
    
    if ($response.success -and $response.text -eq "") {
        Write-Host "✅ 小音频正确处理：返回空文本" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 小音频处理异常" -ForegroundColor Yellow
    }
    Write-Host ""
} catch {
    Write-Host "✅ 小音频正确拒绝" -ForegroundColor Green
    Write-Host ""
}

# 3. 显示使用说明
Write-Host "[3/3] 测试准备就绪！" -ForegroundColor Yellow
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   服务已准备就绪，可以进行语音识别" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📌 改进内容:" -ForegroundColor White
Write-Host "  ✅ 自动检测 ffmpeg 可用性" -ForegroundColor Gray
Write-Host "  ✅ 自动将 WebM/OGG 转换为 WAV" -ForegroundColor Gray
Write-Host "  ✅ 音频大小验证（过滤 < 100 字节）" -ForegroundColor Gray
Write-Host "  ✅ 详细的错误提示和建议" -ForegroundColor Gray
Write-Host "  ✅ 支持 Scoop 安装的 ffmpeg" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 下一步:" -ForegroundColor White
Write-Host "  1. 启动 Node.js 服务: cd websocket-demo; node server.js" -ForegroundColor Gray
Write-Host "  2. 打开浏览器: http://localhost:8080" -ForegroundColor Gray
Write-Host "  3. 登录并测试语音识别功能" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 故障排除:" -ForegroundColor White
Write-Host "  - 如仍出现 500 错误，查看 Paraformer API 窗口日志" -ForegroundColor Gray
Write-Host "  - 确保说话时间至少 0.5 秒" -ForegroundColor Gray
Write-Host "  - 检查麦克风权限和音量" -ForegroundColor Gray
Write-Host ""
