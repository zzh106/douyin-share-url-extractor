# douyin-web-exporter

一个简单易用的 Web 工具，用于提取抖音用户所有公开视频的标题和分享链接。

## ✨ 功能特点

- 🔍 通过用户主页 URL 或 `sec_user_id` 提取视频
- 📋 自动分页获取所有公开视频
- 📥 一键导出为 TXT 文件
- 🎨 简洁美观的深色主题界面
- 🚀 无需登录，无需数据库

## 📁 项目结构

```
douyin-web-exporter/
│── backend/
│   │── app.py             # Flask 后端服务
│   │── douyin_api.py      # 抖音 API 调用模块
│   │── requirements.txt   # Python 依赖
│
│── frontend/
│   │── index.html         # 前端页面
│   │── script.js          # 前端逻辑
│   │── style.css          # 样式文件
│
│── README.md
│── .gitignore
```

## 🛠 技术栈

- **后端**: Flask + Requests
- **前端**: 原生 HTML + JavaScript + CSS
- **API**: 抖音官方 Web API

## 📦 安装与运行

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 3. 打开前端页面

直接在浏览器中打开 `frontend/index.html` 文件即可。

**注意**: 由于浏览器的 CORS 策略，如果直接打开 HTML 文件，可能会遇到跨域问题。建议使用以下方式之一：

#### 方式一：使用 Python 简单 HTTP 服务器

```bash
cd frontend
python -m http.server 8000
```

然后在浏览器中访问 `http://localhost:8000`

#### 方式二：使用 VS Code Live Server 插件

安装 Live Server 插件后，右键点击 `index.html` 选择 "Open with Live Server"

## 📖 使用说明

### 如何获取 sec_user_id

1. 打开抖音网页版，访问目标用户的主页
2. 在浏览器地址栏中，URL 格式通常为：
   - `https://www.douyin.com/user/xxx?sec_user_id=MS4wLjABAAAA...`
   - 其中 `MS4wLjABAAAA...` 就是 `sec_user_id`

3. 或者直接复制整个用户主页 URL，工具会自动提取 `sec_user_id`

### 使用步骤

1. 在输入框中输入：
   - 用户主页完整 URL（推荐）
   - 或直接输入 `sec_user_id`

2. 点击"开始提取"按钮

3. 等待提取完成，视频列表将显示在页面上

4. 点击"导出 TXT"按钮，浏览器会自动下载 `douyin_links.txt` 文件

### 使用示例

**输入示例 1**（完整 URL）:
```
https://www.douyin.com/user/MS4wLjABAAAAxxx?sec_user_id=MS4wLjABAAAAxxx
```

**输入示例 2**（仅 sec_user_id）:
```
MS4wLjABAAAAxxx
```

**导出的 TXT 文件格式**:
```
1. 视频标题1
https://www.douyin.com/video/1234567890

2. 视频标题2
https://www.douyin.com/video/0987654321

...
```

## 🔧 API 接口

### POST /api/fetch_user_videos

获取用户的所有视频列表。

**请求体**:
```json
{
  "sec_user_id": "MS4wLjABAAAAxxx"
}
```

**响应**:
```json
[
  {
    "title": "视频标题",
    "url": "https://www.douyin.com/video/1234567890"
  },
  ...
]
```

### GET /health

健康检查接口。

**响应**:
```json
{
  "status": "ok"
}
```

## ⚠️ 注意事项

1. **网络连接**: 确保能够访问抖音网站
2. **API 限制**: 抖音 API 可能有访问频率限制，如遇到 403 错误，请稍后再试
3. **数据准确性**: 本工具仅提取公开视频，私密视频无法获取
4. **浏览器兼容性**: 建议使用 Chrome、Firefox 或 Edge 等现代浏览器

## 🐛 常见问题

### Q: 提示"网络请求失败"怎么办？

A: 检查后端服务是否正常运行，确保后端在 `http://localhost:5000` 可访问。

### Q: 提示"API 返回错误"怎么办？

A: 可能是 `sec_user_id` 不正确，或者抖音 API 暂时不可用。请检查输入的 `sec_user_id` 是否正确。

### Q: 提取的视频数量为 0？

A: 可能是该用户没有公开视频，或者 `sec_user_id` 不正确。

### Q: 如何解决跨域问题？

A: 使用 Python HTTP 服务器或 Live Server 打开前端页面，而不是直接双击 HTML 文件。

## 📝 开发说明

- 后端使用 Flask 框架，支持 CORS 跨域请求
- 前端使用原生 JavaScript，无需构建工具
- 代码结构清晰，注释完整，便于维护和扩展

## 📄 许可证

本项目仅供学习交流使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

