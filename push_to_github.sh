#!/bin/bash
# 推送到 GitHub 的脚本
# 使用方法: ./push_to_github.sh YOUR_GITHUB_USERNAME

if [ -z "$1" ]; then
    echo "❌ 错误: 请提供你的 GitHub 用户名"
    echo "使用方法: ./push_to_github.sh YOUR_GITHUB_USERNAME"
    echo ""
    echo "或者手动执行以下命令:"
    echo "  git remote set-url origin https://github.com/YOUR_USERNAME/douyin-web-exporter.git"
    echo "  git push -u origin main"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_URL="https://github.com/${GITHUB_USERNAME}/douyin-web-exporter.git"

echo "📦 更新远程仓库 URL..."
git remote set-url origin "$REPO_URL"

echo "📤 推送到 GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ 成功推送到 GitHub!"
    echo "🔗 仓库地址: $REPO_URL"
else
    echo "❌ 推送失败，请确保:"
    echo "   1. 已在 GitHub 上创建了名为 'douyin-web-exporter' 的仓库"
    echo "   2. 已配置了 GitHub 认证（Personal Access Token 或 SSH key）"
    echo ""
    echo "如果还没有创建仓库，请访问: https://github.com/new"
    echo "仓库名称: douyin-web-exporter"
fi

