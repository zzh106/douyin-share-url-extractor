# API 使用说明

## 接口说明

### POST /api/fetch_user_videos

获取用户发布的所有视频的 share_url 列表。

#### 请求参数

```json
{
  "sec_user_id": "MS4wLjABAAAA...",     // 必需：用户 sec_user_id 或主页 URL
  "access_token": "...",                // 可选：Douyin 开放平台 access_token
  "cookie": "...",                      // 可选：浏览器 Cookie 字符串
  "use_browser": false,                 // 可选：是否强制使用浏览器方式（默认 false）
  "fallback_to_browser": true           // 可选：API 失败时是否回退到浏览器方式（默认 true）
}
```

#### 响应格式

```json
{
  "videos": [
    {
      "title": "视频标题",
      "share_url": "https://www.douyin.com/video/1234567890",
      "create_time": "2024-01-01 12:00:00",
      "aweme_id": "1234567890"
    },
    ...
  ],
  "count": 10,
  "method": "api"  // "api" | "browser" | "browser_fallback"
}
```

## 使用方式

### 方式 1: API 方式（优先）

使用 Douyin Web API 获取视频列表，速度较快。

**优点：**
- 速度快
- 资源占用少
- 可以获取更多元数据（如发布时间）

**缺点：**
- 可能需要 Cookie 或 access_token
- 可能被限制访问

**示例：**

```bash
curl -X POST http://localhost:5001/api/fetch_user_videos \
  -H "Content-Type: application/json" \
  -d '{
    "sec_user_id": "MS4wLjABAAAA...",
    "cookie": "你的Cookie值"
  }'
```

### 方式 2: 浏览器自动化（备用）

当 API 方式失败时，自动使用 Playwright 浏览器自动化。

**优点：**
- 更稳定，模拟真实浏览器
- 可以处理需要登录的情况
- 不受 API 限制影响

**缺点：**
- 速度较慢
- 资源占用较大
- 需要安装 Playwright

**强制使用浏览器方式：**

```bash
curl -X POST http://localhost:5001/api/fetch_user_videos \
  -H "Content-Type: application/json" \
  -d '{
    "sec_user_id": "MS4wLjABAAAA...",
    "use_browser": true,
    "cookie": "你的Cookie值"
  }'
```

## 获取 Cookie

1. 在浏览器中登录抖音：https://www.douyin.com
2. 按 F12 打开开发者工具
3. 切换到 Network 标签
4. 访问任意用户主页
5. 找到对 `aweme/post` 的请求
6. 在请求头中找到 `Cookie` 字段
7. 复制完整的 Cookie 值

## 获取 access_token

如果使用 Douyin 开放平台：

1. 访问 Douyin 开放平台：https://open.douyin.com
2. 创建应用并获取 access_token
3. 在请求中传入 `access_token` 参数

## 安装 Playwright（浏览器方式需要）

```bash
pip install playwright
playwright install chromium
```

## 错误处理

- API 方式失败时，如果 `fallback_to_browser` 为 `true`，会自动切换到浏览器方式
- 如果两种方式都失败，会返回详细的错误信息

## 注意事项

1. **Cookie 格式**：Cookie 字符串格式为 `key1=value1; key2=value2; ...`
2. **sec_user_id 格式**：可以是完整的用户主页 URL 或单独的 sec_user_id
3. **请求频率**：建议控制请求频率，避免被限制
4. **数据准确性**：仅能获取公开视频，私密视频无法获取

