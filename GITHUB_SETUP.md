# GitHub 上传指南

## 📋 准备工作

### 1. 在 GitHub 上创建仓库

如果还没有创建仓库，请访问：https://github.com/new

- **仓库名称**: `douyin-web-exporter`
- **描述**: 抖音视频链接导出工具
- **可见性**: Public 或 Private（根据你的需要）
- **不要** 初始化 README、.gitignore 或 license（我们已经有了）

### 2. 配置 Git 用户信息（如果还没有配置）

```bash
git config --global user.name "你的名字"
git config --global user.email "your.email@example.com"
```

## 🚀 推送方式

### 方式一：使用推送脚本（推荐）

```bash
./push_to_github.sh YOUR_GITHUB_USERNAME
```

将 `YOUR_GITHUB_USERNAME` 替换为你的 GitHub 用户名。

### 方式二：手动推送

#### 步骤 1: 更新远程仓库 URL

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/douyin-web-exporter.git
```

将 `YOUR_USERNAME` 替换为你的 GitHub 用户名。

#### 步骤 2: 推送到 GitHub

```bash
git push -u origin main
```

## 🔐 认证方式

### 使用 Personal Access Token (推荐)

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：至少需要 `repo` 权限
4. 生成 token 后，在推送时输入用户名和 token（作为密码）

### 使用 SSH Key

1. 生成 SSH key（如果还没有）:
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```

2. 将公钥添加到 GitHub:
   - 复制公钥: `cat ~/.ssh/id_ed25519.pub`
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key" 并添加

3. 使用 SSH URL:
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/douyin-web-exporter.git
   ```

## ✅ 验证

推送成功后，访问你的仓库：
```
https://github.com/YOUR_USERNAME/douyin-web-exporter
```

## 🐛 常见问题

### Q: 提示 "remote: Support for password authentication was removed"
A: GitHub 不再支持密码认证，请使用 Personal Access Token 或 SSH key。

### Q: 提示 "repository not found"
A: 请确保：
1. 已在 GitHub 上创建了仓库
2. 仓库名称拼写正确
3. 有访问该仓库的权限

### Q: 提示 "Permission denied"
A: 请检查：
1. GitHub 认证配置是否正确
2. 是否有该仓库的写入权限

