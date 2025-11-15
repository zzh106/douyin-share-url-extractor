# 更新日志

## v2.0.0 - 专业版重写

### 🎉 重大更新

#### 1. 双方案支持
- ✅ **API 方式**（优先）：使用 Douyin Web API，速度快，资源占用少
- ✅ **浏览器自动化**（备用）：使用 Playwright，更稳定可靠
- ✅ **自动回退**：API 失败时自动切换到浏览器方式

#### 2. 提取 share_url
- ✅ 从 API 响应中提取真实的 `share_url`（不再自己构建）
- ✅ 支持多种 share_url 字段路径：`share_info.share_url`、`share_url`、`video.share_url`
- ✅ 如果 API 没有提供 share_url，则构建标准 URL

#### 3. 认证支持
- ✅ 支持 Douyin 开放平台 `access_token`
- ✅ 支持浏览器 `Cookie` 认证
- ✅ 自动处理认证失败情况

#### 4. 命令行工具
- ✅ 新增 `fetch_videos.py` 命令行脚本
- ✅ 支持多种输出格式：详细、JSON、仅 URL 列表
- ✅ 支持保存到文件

#### 5. 数据增强
- ✅ 提取视频发布时间（`create_time`）
- ✅ 提取视频 ID（`aweme_id`）
- ✅ 前端显示发布时间信息

#### 6. 错误处理
- ✅ 改进的错误提示
- ✅ 自动重试机制
- ✅ 详细的错误码处理

### 📝 新增文件

- `backend/browser_scraper.py` - 浏览器自动化模块
- `backend/fetch_videos.py` - 命令行工具
- `backend/README_API.md` - API 使用文档

### 🔧 改进的文件

- `backend/douyin_api.py` - 完全重写，支持 share_url 提取
- `backend/app.py` - 支持双方案自动切换
- `frontend/script.js` - 支持新的响应格式和 share_url
- `frontend/style.css` - 添加发布时间样式
- `backend/requirements.txt` - 添加 Playwright 依赖

### 📦 依赖更新

- 新增：`playwright==1.40.0`

### 🚀 使用方式

#### 命令行（推荐）
```bash
python backend/fetch_videos.py MS4wLjABAAAA...
```

#### Web 界面
```bash
# 启动后端
python backend/app.py

# 启动前端
cd frontend && python -m http.server 8000
```

### ⚠️ 注意事项

1. **首次使用浏览器方式需要安装 Playwright**：
   ```bash
   playwright install chromium
   ```

2. **Cookie 格式**：`key1=value1; key2=value2; ...`

3. **API 方式可能需要 Cookie**：如果 API 返回空响应，请提供 Cookie

4. **浏览器方式较慢**：但更稳定，适合大量视频提取

### 🔄 迁移指南

#### 从 v1.x 升级

1. **安装新依赖**：
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **API 响应格式变化**：
   - 旧格式：`[{"title": "...", "url": "..."}]`
   - 新格式：`{"videos": [...], "count": 10, "method": "api"}`

3. **字段名称变化**：
   - `url` → `share_url`（兼容旧字段）

### 🐛 已知问题

- Playwright 首次安装需要下载浏览器（约 200MB）
- 浏览器方式在无头模式下可能无法处理某些动态加载内容

### 📚 文档

- 详细 API 文档：`backend/README_API.md`
- 故障排除：`TROUBLESHOOTING.md`
- 快速开始：`QUICKSTART.md`

