# douyin-web-exporter 使用指南

## 🚀 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip3 install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
python3 app.py
```

后端服务将在 `http://localhost:5000` 启动。

**注意**: 保持这个终端窗口打开，后端服务需要持续运行。

### 3. 打开前端页面

#### 方式一：使用 Python HTTP 服务器（推荐）

打开新的终端窗口：

```bash
cd frontend
python3 -m http.server 8000
```

然后在浏览器中访问：`http://localhost:8000`

#### 方式二：使用 VS Code Live Server

1. 安装 VS Code 的 "Live Server" 插件
2. 右键点击 `frontend/index.html`
3. 选择 "Open with Live Server"

#### 方式三：直接打开（可能遇到跨域问题）

直接双击 `frontend/index.html` 文件，但可能会遇到跨域问题。

## 📖 使用步骤

### 步骤 1: 获取 sec_user_id

1. 打开抖音网页版：https://www.douyin.com
2. 访问目标用户的主页
3. 在浏览器地址栏中，URL 格式通常为：
   ```
   https://www.douyin.com/user/xxx?sec_user_id=MS4wLjABAAAA...
   ```
   其中 `MS4wLjABAAAA...` 就是 `sec_user_id`

4. 或者直接复制整个用户主页 URL

### 步骤 2: 提取视频

1. 在前端页面的输入框中输入：
   - **方式一**：完整的用户主页 URL（推荐）
     ```
     https://www.douyin.com/user/xxx?sec_user_id=MS4wLjABAAAA...
     ```
   - **方式二**：直接输入 `sec_user_id`
     ```
     MS4wLjABAAAA...
     ```

2. 点击"开始提取"按钮

3. 等待提取完成（会显示加载动画）

4. 视频列表将显示在页面上，包括：
   - 序号
   - 视频标题
   - 视频链接（可点击）

### 步骤 3: 导出 TXT

1. 点击"导出 TXT"按钮
2. 浏览器会自动下载 `douyin_links.txt` 文件
3. 文件格式：
   ```
   1. 视频标题1
   https://www.douyin.com/video/1234567890

   2. 视频标题2
   https://www.douyin.com/video/0987654321
   ...
   ```

## 🔧 API 使用（开发者）

### 健康检查

```bash
curl http://localhost:5000/health
```

响应：
```json
{"status": "ok"}
```

### 获取用户视频

```bash
curl -X POST http://localhost:5000/api/fetch_user_videos \
  -H "Content-Type: application/json" \
  -d '{"sec_user_id": "MS4wLjABAAAA..."}'
```

响应：
```json
[
  {
    "title": "视频标题",
    "url": "https://www.douyin.com/video/1234567890"
  },
  ...
]
```

## ⚠️ 注意事项

1. **后端服务必须运行**：前端需要后端 API 才能工作
2. **网络连接**：确保能够访问抖音网站
3. **API 限制**：抖音 API 可能有访问频率限制，如遇到 403 错误，请稍后再试
4. **数据准确性**：本工具仅提取公开视频，私密视频无法获取
5. **浏览器兼容性**：建议使用 Chrome、Firefox 或 Edge 等现代浏览器

## 🐛 常见问题

### Q: 提示"网络请求失败"怎么办？

**A**: 检查以下几点：
1. 后端服务是否在运行（`python3 app.py`）
2. 后端服务是否在 `http://localhost:5000`
3. 浏览器控制台是否有错误信息（按 F12 打开开发者工具）

### Q: 提示"API 返回错误"怎么办？

**A**: 可能的原因：
1. `sec_user_id` 不正确
2. 抖音 API 暂时不可用
3. 网络连接问题

**解决方法**：
- 检查输入的 `sec_user_id` 是否正确
- 稍后再试
- 检查网络连接

### Q: 提取的视频数量为 0？

**A**: 可能的原因：
1. 该用户没有公开视频
2. `sec_user_id` 不正确
3. 抖音 API 返回了空数据

**解决方法**：
- 确认用户有公开视频
- 重新获取正确的 `sec_user_id`
- 尝试其他用户

### Q: 如何解决跨域问题？

**A**: 使用 Python HTTP 服务器或 Live Server 打开前端页面，而不是直接双击 HTML 文件。

### Q: 后端服务启动失败？

**A**: 检查：
1. Python 版本（需要 Python 3.7+）
2. 依赖是否已安装（`pip3 install -r requirements.txt`）
3. 端口 5000 是否被占用

## 📝 项目结构

```
douyin-web-exporter/
├── backend/              # 后端代码
│   ├── app.py           # Flask 服务
│   ├── douyin_api.py    # 抖音 API 调用
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端代码
│   ├── index.html       # 主页面
│   ├── script.js        # 前端逻辑
│   └── style.css        # 样式文件
└── README.md            # 项目说明
```

## 🎯 使用示例

### 完整示例

1. **启动后端**（终端 1）：
   ```bash
   cd backend
   python3 app.py
   ```

2. **启动前端服务器**（终端 2）：
   ```bash
   cd frontend
   python3 -m http.server 8000
   ```

3. **打开浏览器**：
   - 访问：`http://localhost:8000`
   - 输入用户主页 URL 或 `sec_user_id`
   - 点击"开始提取"
   - 等待结果
   - 点击"导出 TXT"

## 🔒 安全提示

- 本工具仅用于提取公开视频信息
- 不涉及视频下载
- 不涉及用户登录
- 所有数据均为公开数据

