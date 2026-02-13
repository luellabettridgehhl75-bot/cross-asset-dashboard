#!/bin/bash
# 自动部署脚本 - 将看板推送到GitHub Pages

REPO_NAME="cross-asset-dashboard"
GITHUB_USER="${GITHUB_USER:-yourusername}"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo "🚀 部署看板到 GitHub Pages..."
echo ""

# 检查是否配置了GitHub用户名
if [ "$GITHUB_USER" = "yourusername" ]; then
    echo "⚠️ 请先设置你的GitHub用户名:"
    echo "   export GITHUB_USER=你的用户名"
    echo ""
    read -p "请输入你的GitHub用户名: " GITHUB_USER
    export GITHUB_USER
fi

# 创建临时目录
cd output

# 初始化git仓库（如果不存在）
if [ ! -d ".git" ]; then
    echo "📦 初始化Git仓库..."
    git init
    git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git" 2>/dev/null || true
fi

# 确保在gh-pages分支
git checkout -b gh-pages 2>/dev/null || git checkout gh-pages

# 复制看板文件
cp ../output/dashboard.html .

# 创建index.html（GitHub Pages入口）
cp dashboard.html index.html

# 添加所有文件
git add -A

# 提交更改
git commit -m "Update dashboard: $(date '+%Y-%m-%d %H:%M:%S')" --allow-empty

# 推送到GitHub
echo "📤 推送到GitHub..."
git push -u origin gh-pages --force

echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "   https://${GITHUB_USER}.github.io/${REPO_NAME}/"
echo ""
echo "📱 手机访问: 直接打开上述链接"
echo ""

# 生成二维码（可选，如果安装qrencode）
if command -v qrencode &> /dev/null; then
    echo "📱 二维码:"
    qrencode -t ANSIUTF8 "https://${GITHUB_USER}.github.io/${REPO_NAME}/"
fi

cd ..
