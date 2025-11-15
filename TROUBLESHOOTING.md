# 故障排除指南

## 问题：抖音 API 返回空响应

如果遇到 "抖音 API 返回空响应" 的错误，这通常是因为抖音 API 需要更完整的浏览器环境或登录状态。

### 解决方案

#### 方案 1: 使用浏览器 Cookie（推荐）

抖音 API 可能需要登录 Cookie 才能正常访问。请按以下步骤操作：

1. **在浏览器中登录抖音**
   - 打开 https://www.douyin.com
   - 登录你的抖音账号

2. **获取 Cookie**
   - 按 F12 打开开发者工具
   - 切换到 "Network"（网络）标签
   - 访问任意用户主页
   - 找到对 `aweme/post` 的请求
   - 在请求头中找到 `Cookie` 字段
   - 复制完整的 Cookie 值

3. **配置 Cookie（需要修改代码）**
   
   修改 `backend/douyin_api.py`，在 `headers` 中添加 Cookie：
   
   ```python
   headers = {
       # ... 其他请求头 ...
       'Cookie': '你的Cookie值'
   }
   ```

#### 方案 2: 检查 sec_user_id 是否正确

1. **获取正确的 sec_user_id**
   - 在浏览器中访问目标用户主页
   - 查看浏览器地址栏，URL 格式应为：
     ```
     https://www.douyin.com/user/xxx?sec_user_id=MS4wLjABAAAA...
     ```
   - 确保复制完整的 `sec_user_id`（通常以 `MS4wLjABAAAA` 开头）

2. **验证 sec_user_id**
   - 在浏览器中直接访问：
     ```
     https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=你的sec_user_id&count=20&max_cursor=0
     ```
   - 如果返回空响应，说明需要 Cookie
   - 如果返回 JSON 数据，说明 sec_user_id 正确

#### 方案 3: 使用其他 API 端点

抖音可能有多个 API 端点，可以尝试：

1. **移动端 API**
   ```
   https://www.iesdouyin.com/aweme/v1/web/aweme/post/...
   ```

2. **不同版本的 API**
   - 尝试不同的 `version_code` 和 `version_name` 参数

#### 方案 4: 使用浏览器自动化（高级）

如果上述方法都不行，可以考虑使用 Selenium 或 Playwright 等浏览器自动化工具：

1. 使用真实浏览器环境
2. 自动登录并获取 Cookie
3. 调用 API 获取数据

### 常见错误码说明

- **10000**: 参数错误，检查 sec_user_id 是否正确
- **10001**: 用户不存在或已注销
- **10002**: 用户设置了隐私，无法访问
- **空响应**: 需要登录 Cookie 或 API 访问被限制

### 调试技巧

1. **查看后端日志**
   ```bash
   tail -f /tmp/douyin_backend.log
   ```

2. **测试 API 直接调用**
   ```bash
   curl -v "https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=你的sec_user_id&count=20&max_cursor=0"
   ```

3. **检查网络连接**
   - 确保能访问 https://www.douyin.com
   - 检查是否有防火墙或代理限制

### 临时解决方案

如果急需使用，可以：

1. 在浏览器中手动访问用户主页
2. 使用浏览器扩展（如油猴脚本）提取视频链接
3. 或者等待抖音 API 策略调整

### 注意事项

- 抖音 API 可能会频繁变更，需要定期更新代码
- 大量请求可能触发反爬虫机制，建议控制请求频率
- 遵守抖音的使用条款，不要用于商业用途

