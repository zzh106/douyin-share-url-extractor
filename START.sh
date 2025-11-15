#!/bin/bash
# 一键启动脚本

echo "🚀 启动 douyin-web-exporter"
echo ""

# 检查后端依赖
cd backend
if ! python3 -c "import flask, requests, flask_cors" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip3 install -r requirements.txt
fi

# 启动后端
echo "🔧 启动后端服务 (端口 5000)..."
python3 app.py &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端
cd ../frontend
echo "🌐 启动前端服务 (端口 8000)..."
python3 -m http.server 8000 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"

echo ""
echo "=========================================="
echo "✅ 服务启动完成！"
echo ""
echo "📋 服务信息:"
echo "   - 后端: http://localhost:5000"
echo "   - 前端: http://localhost:8000"
echo ""
echo "🌐 请在浏览器中访问: http://localhost:8000"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "=========================================="
