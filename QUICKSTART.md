# 🚀 快速开始指南

## 三步启动项目

### 步骤 1: 启动后端服务

打开终端，运行：

```bash
cd backend
python3 app.py
```

**看到以下输出表示启动成功：**
```
启动 Flask 服务器...
API 地址: http://localhost:5000/api/fetch_user_videos
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

**⚠️ 注意**: 保持这个终端窗口打开！

---

### 步骤 2: 启动前端服务器

**打开新的终端窗口**，运行：

```bash
cd frontend
python3 -m http.server 8000
```

**看到以下输出表示启动成功：**
```
Serving HTTP on :: port 8000 (http://[::]:8000/) ...
```

---

### 步骤 3: 打开浏览器

访问：**http://localhost:8000**

---

## 📝 使用流程

### 1. 获取 sec_user_id

1. 打开抖音网页版：https://www.douyin.com
2. 访问目标用户主页
3. 复制浏览器地址栏的 URL，例如：
   ```
   https://www.douyin.com/user/xxx?sec_user_id=MS4wLjABAAAA...
   ```

### 2. 提取视频

1. 在页面输入框中粘贴刚才复制的 URL（或直接输入 `sec_user_id`）
2. 点击"开始提取"按钮
3. 等待提取完成（会显示加载动画）

### 3. 导出 TXT

1. 提取完成后，点击"导出 TXT"按钮
2. 浏览器会自动下载 `douyin_links.txt` 文件

---

## 🔧 测试服务是否正常

### 测试后端服务

在**新的终端窗口**运行：

```bash
# 测试健康检查
curl http://localhost:5000/health

# 应该返回: {"status":"ok"}
```

### 测试 API 接口

```bash
curl -X POST http://localhost:5000/api/fetch_user_videos \
  -H "Content-Type: application/json" \
  -d '{"sec_user_id":"test"}'
```

---

## ⚠️ 常见问题

### 问题 1: 端口 5000 被占用

**错误信息：**
```
Address already in use
Port 5000 is in use by another program.
```

**解决方法：**

**macOS 用户：**
1. 打开"系统设置" → "通用" → "隔空播放与接力"
2. 关闭"隔空播放接收器"

**或者修改端口：**
编辑 `backend/app.py`，将最后一行改为：
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 改为 5001
```

同时修改 `frontend/script.js`，将：
```javascript
const API_BASE_URL = 'http://localhost:5000';
```
改为：
```javascript
const API_BASE_URL = 'http://localhost:5001';
```

### 问题 2: 前端无法连接后端

**检查清单：**
- ✅ 后端服务是否在运行？
- ✅ 后端是否在 `http://localhost:5000`？
- ✅ 前端是否通过 HTTP 服务器打开（不是直接双击 HTML）？

### 问题 3: 提示"网络请求失败"

**解决方法：**
1. 检查后端服务是否正常运行
2. 打开浏览器开发者工具（F12），查看 Console 中的错误信息
3. 确认后端服务地址是否正确

---

## 📋 完整命令示例

### 终端 1（后端）:
```bash
cd /Users/zzh/Projects/DouyinSearchDownloader/backend
python3 app.py
```

### 终端 2（前端）:
```bash
cd /Users/zzh/Projects/DouyinSearchDownloader/frontend
python3 -m http.server 8000
```

### 浏览器:
访问 `http://localhost:8000`

---

## 🎯 成功标志

✅ 后端服务：终端显示 "Running on http://0.0.0.0:5000"  
✅ 前端服务：终端显示 "Serving HTTP on :: port 8000"  
✅ 浏览器：页面正常显示，可以输入和提交  
✅ API 测试：`curl http://localhost:5000/health` 返回 `{"status":"ok"}`

---

## 📚 更多信息

详细使用说明请查看：`USAGE.md`  
项目说明请查看：`README.md`

