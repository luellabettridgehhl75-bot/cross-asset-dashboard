#!/bin/bash
# 完整部署脚本 - 保存并运行此脚本

echo "🚀 开始部署到 GitHub Pages..."
echo ""

# 1. 获取 GitHub 用户名
echo "📋 步骤1: 配置GitHub"
read -p "请输入你的GitHub用户名: " GITHUB_USER
read -p "请输入你的GitHub邮箱: " GITHUB_EMAIL

# 2. 配置 git
git config user.name "$GITHUB_USER"
git config user.email "$GITHUB_EMAIL"

# 3. 创建 GitHub 仓库
echo ""
echo "📦 步骤2: 在GitHub创建仓库"
echo "请打开: https://github.com/new"
echo "仓库名: cross-asset-dashboard"
echo "设置为 Public"
echo "不要勾选 README"
echo ""
read -p "按回车继续..."

# 4. 添加远程仓库
echo ""
echo "🔗 步骤3: 连接远程仓库"
git remote add origin "https://github.com/$GITHUB_USER/cross-asset-dashboard.git" 2>/dev/null || \
git remote set-url origin "https://github.com/$GITHUB_USER/cross-asset-dashboard.git"

# 5. 推送代码
echo ""
echo "📤 步骤4: 推送代码"
echo "首次推送需要GitHub认证，请在浏览器中完成登录..."
git push -u origin main

echo ""
echo "✅ 代码已推送！"
echo ""

# 6. 开启 GitHub Pages
echo "🌐 步骤5: 开启GitHub Pages"
echo "请打开: https://github.com/$GITHUB_USER/cross-asset-dashboard/settings/pages"
echo "Source 选择: GitHub Actions"
echo ""
read -p "完成设置后按回车..."

echo ""
echo "🎉 部署完成！"
echo ""
echo "📱 手机访问地址:"
echo "   https://$GITHUB_USER.github.io/cross-asset-dashboard/"
echo ""
echo "⏰ 自动更新: 美股时段每小时自动刷新数据"
echo ""
