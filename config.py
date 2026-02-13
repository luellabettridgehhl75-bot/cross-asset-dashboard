"""
配置文件 - 跨资产实时监控系统
"""

# ==========================================
# 资产列表配置
# ==========================================

# 美股 - 科技七姐妹 + 主要ETF
US_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corp.',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corp.',
    'META': 'Meta Platforms Inc.',
    'TSLA': 'Tesla Inc.',
    'SPY': 'S&P 500 ETF',
    'QQQ': 'Nasdaq-100 ETF',
    'IWM': 'Russell 2000 ETF',
    'VTI': 'Total Stock Market ETF',
}

# 贵金属
PRECIOUS_METALS = {
    'GLD': '黄金 ETF',
    'SLV': '白银 ETF',
    'PPLT': '铂金 ETF',
    'PALL': '钯金 ETF',
}

# 能源
ENERGY = {
    'USO': 'WTI原油 ETF',
    'BNO': '布伦特原油 ETF',
    'UNG': '天然气 ETF',
}

# 大宗商品
COMMODITIES = {
    'JJC': '铜 ETF',
    'JJU': '铝 ETF',
    'REMX': '稀土 ETF',
}

# 加密货币 (使用Binance交易对)
CRYPTO = {
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'SOL-USD': 'Solana',
    'WLD-USD': 'Worldcoin',
}

# 宏观指标
MACRO = {
    '^VIX': 'VIX波动率指数',
    'UUP': '美元指数 ETF',
    'TLT': '20+年美债 ETF',
    'SHY': '1-3年美债 ETF',
    'LQD': '投资级公司债 ETF',
    'HYG': '高收益债 ETF',
}

# 所有资产合并
ALL_ASSETS = {
    'us_stocks': US_STOCKS,
    'precious_metals': PRECIOUS_METALS,
    'energy': ENERGY,
    'commodities': COMMODITIES,
    'crypto': CRYPTO,
    'macro': MACRO,
}

# 资产类别显示名称
CATEGORY_NAMES = {
    'us_stocks': '美股',
    'precious_metals': '贵金属',
    'energy': '能源',
    'commodities': '大宗商品',
    'crypto': '加密货币',
    'macro': '宏观指标',
}

# ==========================================
# 技术指标配置
# ==========================================

# 均线周期
MA_SHORT = 10  # 短期均线
MA_LONG = 50   # 长期均线

# 趋势判断阈值
TREND_THRESHOLD = 0.02  # 2%变动视为趋势变化

# 震荡区间阈值
CONSOLIDATION_THRESHOLD = 0.03  # 3%内视为震荡

# ==========================================
# Telegram 配置
# ==========================================

TELEGRAM_BOT_TOKEN = ""  # 填入你的Bot Token
TELEGRAM_CHAT_ID = ""    # 填入你的Chat ID

# ==========================================
# 输出配置
# ==========================================

OUTPUT_DIR = "output"
HTML_FILENAME = "dashboard.html"
UPDATE_INTERVAL = 3600  # 更新间隔（秒）

# ==========================================
# 数据源配置
# ==========================================

# Yahoo Finance 配置
YF_PERIOD = "1y"  # 获取1年历史数据
YF_INTERVAL = "1d"  # 日线数据

# Binance API 配置 (用于加密货币)
BINANCE_BASE_URL = "https://api.binance.com"
