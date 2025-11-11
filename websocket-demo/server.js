const WebSocket = require("ws");
const http = require("http");

// 创建 HTTP 服务器
const server = http.createServer();
const wss = new WebSocket.Server({ server });

wss.on("connection", (ws) => {
  ws.send(
    JSON.stringify({
      type: "info",
      message: "[此处为预留接口，未接入任何业务逻辑]",
    })
  );
});

// 启动服务器
const PORT = 8080;
server.listen(PORT, () => {
  console.log(`WebSocket 预留服务已启动，端口 ${PORT}`);
});
