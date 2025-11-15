#!/bin/bash
# 测试服务器脚本

echo "🧪 测试 douyin-web-exporter 后端服务"
echo ""

# 检查依赖
echo "1. 检查 Python 依赖..."
cd backend
if ! python3 -c "import flask, requests, flask_cors" 2>/dev/null; then
    echo "❌ 依赖未安装，正在安装..."
    pip3 install -r requirements.txt
else
    echo "✅ 依赖已安装"
fi

# 启动服务器（后台）
echo ""
echo "2. 启动后端服务..."
python3 app.py > /tmp/douyin_server.log 2>&1 &
SERVER_PID=$!
echo "   服务 PID: $SERVER_PID"

# 等待服务启动
echo "   等待服务启动..."
sleep 3

# 测试健康检查
echo ""
echo "3. 测试健康检查接口..."
HEALTH_RESPONSE=$(curl -s http://localhost:5000/health 2>&1)
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "   ✅ 健康检查通过: $HEALTH_RESPONSE"
else
    echo "   ❌ 健康检查失败: $HEALTH_RESPONSE"
fi

# 测试 API 接口（使用测试 sec_user_id）
echo ""
echo "4. 测试 API 接口..."
API_RESPONSE=$(curl -s -X POST http://localhost:5000/api/fetch_user_videos \
    -H "Content-Type: application/json" \
    -d '{"sec_user_id":"test"}' 2>&1)

if echo "$API_RESPONSE" | grep -q "error"; then
    echo "   ✅ API 接口响应正常（返回错误是预期的，因为测试 sec_user_id 无效）"
    echo "   响应: $(echo $API_RESPONSE | head -c 100)..."
else
    echo "   ⚠️  API 响应: $(echo $API_RESPONSE | head -c 100)..."
fi

# 显示服务日志
echo ""
echo "5. 服务日志（最后 10 行）:"
tail -10 /tmp/douyin_server.log 2>/dev/null || echo "   无日志"

echo ""
echo "=========================================="
echo "✅ 测试完成！"
echo ""
echo "📋 服务状态:"
echo "   - 后端服务运行在: http://localhost:5000"
echo "   - 服务 PID: $SERVER_PID"
echo ""
echo "📖 使用方法:"
echo "   1. 保持此终端运行（或后台运行服务）"
echo "   2. 打开新终端，运行: cd frontend && python3 -m http.server 8000"
echo "   3. 在浏览器访问: http://localhost:8000"
echo ""
echo "🛑 停止服务: kill $SERVER_PID"
echo "=========================================="

