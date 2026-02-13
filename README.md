# 跨资产实时监控系统

## 项目结构
```
cross_asset_monitor/
├── data_fetcher.py      # 数据抓取模块
├── indicators.py        # 技术指标计算
├── dashboard.py         # HTML看板生成
├── telegram_bot.py      # Telegram推送
├── config.py           # 配置文件
├── main.py             # 主程序入口
├── requirements.txt    # 依赖包
└── output/             # 输出目录
    └── dashboard.html  # 生成的看板
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 配置Telegram Bot
1. 在 Telegram 中搜索 @BotFather
2. 创建新机器人，获取 token
3. 将 token 填入 config.py

## 运行
```bash
python main.py
```

## 定时运行（crontab）
```bash
# 每小时运行一次
0 * * * * cd /path/to/cross_asset_monitor && python main.py
```

## 🌐 部署到 GitHub Pages（手机随时访问）

### 方式一：GitHub Actions自动部署（推荐）

1. **创建GitHub仓库**
   - 登录GitHub → New Repository → 命名如 `cross-asset-dashboard`
   - 仓库设为 Public（免费托管）

2. **推送代码到GitHub**
```bash
git init
git remote add origin https://github.com/你的用户名/cross-asset-dashboard.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

3. **开启GitHub Pages**
   - 进入仓库 → Settings → Pages
   - Source 选择 "GitHub Actions"
   - 等待部署完成（约2分钟）

4. **访问看板**
   - 手机浏览器打开：`https://你的用户名.github.io/cross-asset-dashboard/`
   - 可以添加到手机主屏幕，像APP一样使用

### 方式二：本地脚本部署
```bash
export GITHUB_USER=你的用户名
./deploy.sh
```

### 自动更新
- GitHub Actions 会在美股交易时段每小时自动更新
- 手机访问永远是最新数据

## 📱 手机访问方式

1. **浏览器书签**：Safari/Chrome 打开GitHub Pages链接
2. **添加到主屏**：iPhone Safari → 分享 → 添加到主屏幕
3. **二维码分享**：部署后可用 qrencode 生成二维码

## ⚠️ 注意事项
- GitHub Pages 免费但有访问频率限制（每天10万次）
- 数据有15分钟延迟（Yahoo Finance限制）
- 仅供学习参考，不构成投资建议
