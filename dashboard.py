"""
HTML看板生成模块 - 专业版
包含：高级指标、迷你图表、热力图、相对强弱排名
"""

import os
from datetime import datetime
from typing import Dict, List, Tuple
import config


class DashboardGenerator:
    """专业版HTML看板生成器"""
    
    def __init__(self, output_dir: str = config.OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_sparkline(self, data_points: List[float], width: int = 100, height: int = 30) -> str:
        """生成迷你走势图 (Sparkline)"""
        if not data_points or len(data_points) < 2:
            return ""
        
        # 归一化数据到SVG坐标
        min_val = min(data_points)
        max_val = max(data_points)
        range_val = max_val - min_val if max_val != min_val else 1
        
        points = []
        for i, val in enumerate(data_points):
            x = (i / (len(data_points) - 1)) * width
            y = height - ((val - min_val) / range_val) * height
            points.append(f"{x:.1f},{y:.1f}")
        
        # 生成SVG polyline
        color = "#4ade80" if data_points[-1] > data_points[0] else "#f87171"
        svg = f'<svg width="{width}" height="{height}" style="overflow: visible;">'
        svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>'
        svg += '</svg>'
        return svg
    
    def _calculate_heatmap_color(self, value: float, min_val: float = -5, max_val: float = 5) -> str:
        """计算热力图颜色"""
        if value > 0:
            intensity = min(value / max_val, 1)
            return f"rgba(74, 222, 128, {0.1 + intensity * 0.4})"  # 绿色
        else:
            intensity = min(abs(value) / abs(min_val), 1)
            return f"rgba(248, 113, 113, {0.1 + intensity * 0.4})"  # 红色
    
    def _generate_market_overview(self, data: Dict) -> str:
        """生成市场概览统计"""
        total_assets = sum(len(assets) for assets in data.values() if assets)
        
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for category, assets in data.items():
            for symbol, info in assets.items():
                if info and 'trend_color' in info:
                    if info['trend_color'] == 'bullish':
                        bullish_count += 1
                    elif info['trend_color'] == 'bearish':
                        bearish_count += 1
                    else:
                        neutral_count += 1
        
        html = f"""
    <div class="market-overview">
        <div class="overview-card">
            <div class="overview-title">📊 市场概览</div>
            <div class="overview-stats">
                <div class="stat-item bullish">
                    <div class="stat-value">{bullish_count}</div>
                    <div class="stat-label">上涨</div>
                </div>
                <div class="stat-item neutral">
                    <div class="stat-value">{neutral_count}</div>
                    <div class="stat-label">震荡</div>
                </div>
                <div class="stat-item bearish">
                    <div class="stat-value">{bearish_count}</div>
                    <div class="stat-label">下跌</div>
                </div>
                <div class="stat-item total">
                    <div class="stat-value">{total_assets}</div>
                    <div class="stat-label">监控资产</div>
                </div>
            </div>
        </div>
    </div>
"""
        return html
    
    def generate_html(self, data: Dict) -> str:
        """生成专业版HTML看板"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>跨资产实时监控系统 - 专业版</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0a0f1a 0%, #151b2b 50%, #0f172a 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 25px;
            padding: 25px 20px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
            border-radius: 16px;
            border: 1px solid rgba(96, 165, 250, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(96, 165, 250, 0.3);
        }}
        
        .header .timestamp {{
            color: #64748b;
            font-size: 14px;
            letter-spacing: 1px;
        }}
        
        /* 市场概览 */
        .market-overview {{
            margin-bottom: 25px;
        }}
        
        .overview-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .overview-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #94a3b8;
        }}
        
        .overview-stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .stat-item.bullish {{ border-color: rgba(74, 222, 128, 0.3); }}
        .stat-item.neutral {{ border-color: rgba(250, 204, 21, 0.3); }}
        .stat-item.bearish {{ border-color: rgba(248, 113, 113, 0.3); }}
        
        .stat-value {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-item.bullish .stat-value {{ color: #4ade80; }}
        .stat-item.neutral .stat-value {{ color: #facc15; }}
        .stat-item.bearish .stat-value {{ color: #f87171; }}
        .stat-item.total .stat-value {{ color: #60a5fa; }}
        
        .stat-label {{
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* 资产分类 */
        .category {{
            margin-bottom: 25px;
        }}
        
        .category-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            padding: 12px 20px;
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.2), transparent);
            border-left: 4px solid #3b82f6;
            border-radius: 0 12px 12px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .assets-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 15px;
        }}
        
        .asset-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.7));
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 16px;
            padding: 18px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .asset-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
            border-color: rgba(96, 165, 250, 0.3);
        }}
        
        .asset-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .asset-card:hover::before {{
            opacity: 1;
        }}
        
        .asset-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        
        .asset-symbol {{
            font-weight: 700;
            font-size: 18px;
            color: #f8fafc;
            letter-spacing: 0.5px;
        }}
        
        .asset-name {{
            font-size: 11px;
            color: #64748b;
            margin-top: 3px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .asset-trend {{
            font-size: 20px;
            background: rgba(15, 23, 42, 0.5);
            padding: 4px 8px;
            border-radius: 8px;
        }}
        
        .price-row {{
            display: flex;
            align-items: baseline;
            gap: 12px;
            margin-bottom: 10px;
        }}
        
        .asset-price {{
            font-size: 26px;
            font-weight: 700;
            color: #f8fafc;
            letter-spacing: 0.5px;
        }}
        
        .asset-change {{
            font-size: 14px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        
        .positive {{
            color: #4ade80;
            background: rgba(74, 222, 128, 0.15);
        }}
        
        .negative {{
            color: #f87171;
            background: rgba(248, 113, 113, 0.15);
        }}
        
        /* 迷你图表 */
        .sparkline-container {{
            margin: 10px 0;
            height: 35px;
            display: flex;
            align-items: center;
        }}
        
        /* 指标网格 */
        .asset-metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .metric {{
            display: flex;
            flex-direction: column;
            padding: 8px;
            background: rgba(15, 23, 42, 0.4);
            border-radius: 8px;
            text-align: center;
        }}
        
        .metric-label {{
            font-size: 10px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 3px;
        }}
        
        .metric-value {{
            font-size: 12px;
            font-weight: 600;
            color: #e2e8f0;
        }}
        
        .metric-value.positive {{ color: #4ade80; }}
        .metric-value.negative {{ color: #f87171; }}
        
        /* RSI 指示器 */
        .rsi-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-left: 5px;
        }}
        
        .rsi-overbought {{ background: #f87171; box-shadow: 0 0 8px #f87171; }}
        .rsi-oversold {{ background: #4ade80; box-shadow: 0 0 8px #4ade80; }}
        .rsi-neutral {{ background: #facc15; }}
        
        /* 52周范围条 */
        .range-bar {{
            width: 100%;
            height: 4px;
            background: rgba(148, 163, 184, 0.2);
            border-radius: 2px;
            margin-top: 5px;
            position: relative;
        }}
        
        .range-indicator {{
            position: absolute;
            width: 2px;
            height: 8px;
            background: #60a5fa;
            top: -2px;
            border-radius: 1px;
            box-shadow: 0 0 4px #60a5fa;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 25px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 16px;
            color: #475569;
            font-size: 12px;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .assets-grid {{
                grid-template-columns: 1fr;
            }}
            .overview-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 跨资产实时监控系统</h1>
        <div class="timestamp">专业版 | 更新时间: {timestamp}</div>
    </div>
"""
        
        # 市场概览
        html += self._generate_market_overview(data)
        
        # 每个资产类别
        for category, assets in data.items():
            if not assets:
                continue
            
            category_name = config.CATEGORY_NAMES.get(category, category)
            html += f"""
    <div class="category">
        <div class="category-title">{category_name}</div>
        <div class="assets-grid">
"""
            
            for symbol, info in assets.items():
                if not info:
                    continue
                
                # 提取数据
                price = info.get('current_price', 0)
                change_pct = info.get('daily_change_pct', 0)
                change = info.get('daily_change', 0)
                trend = info.get('trend', '🟡')
                trend_color = info.get('trend_color', 'neutral')
                ytd = info.get('ytd_return', 0)
                ma10 = info.get('ma_10', 0)
                ma50 = info.get('ma_50', 0)
                rsi = info.get('rsi', 50)
                volatility = info.get('volatility', 0)
                high_52w = info.get('high_52w', price)
                low_52w = info.get('low_52w', price)
                rel = info.get('relative_strength', 'Moderate')
                
                # 颜色类
                change_class = 'positive' if change_pct >= 0 else 'negative'
                ytd_class = 'positive' if ytd >= 0 else 'negative'
                change_sign = '+' if change_pct >= 0 else ''
                
                # RSI 状态
                rsi_class = 'rsi-overbought' if rsi > 70 else ('rsi-oversold' if rsi < 30 else 'rsi-neutral')
                rsi_text = '超买' if rsi > 70 else ('超卖' if rsi < 30 else '正常')
                
                # 52周位置
                week_range = high_52w - low_52w if high_52w != low_52w else 1
                week_position = ((price - low_52w) / week_range) * 100
                
                html += f"""
            <div class="asset-card">
                <div class="asset-header">
                    <div>
                        <div class="asset-symbol">{symbol}</div>
                        <div class="asset-name">{info.get('name', '')}</div>
                    </div>
                    <div class="asset-trend">{trend}</div>
                </div>
                <div class="price-row">
                    <div class="asset-price">${price:,.2f}</div>
                    <span class="asset-change {change_class}">
                        {change_sign}{change_pct:.2f}%
                    </span>
                </div>
                <div class="asset-metrics">
                    <div class="metric">
                        <span class="metric-label">YTD</span>
                        <span class="metric-value {ytd_class}">{ytd:+.1f}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">RSI({rsi:.0f})</span>
                        <span class="metric-value">{rsi_text}<span class="rsi-indicator {rsi_class}"></span></span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">波动率</span>
                        <span class="metric-value">{volatility:.1f}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">MA10</span>
                        <span class="metric-value">${ma10:,.2f}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">MA50</span>
                        <span class="metric-value">${ma50:,.2f}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">相对强弱</span>
                        <span class="metric-value">{rel}</span>
                    </div>
                </div>
                <div style="margin-top: 8px;">
                    <div style="font-size: 10px; color: #64748b; margin-bottom: 3px;">52周区间</div>
                    <div class="range-bar">
                        <div class="range-indicator" style="left: {week_position:.1f}%;"></div>
                    </div>
                </div>
            </div>
"""
            
            html += """
        </div>
    </div>
"""
        
        html += """
    <div class="footer">
        <p>📈 跨资产实时监控系统 专业版 v1.0</p>
        <p>数据来源: Yahoo Finance | 更新频率: 每小时</p>
        <p style="margin-top: 10px; color: #64748b;">⚠️ 仅供参考，不构成投资建议</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_dashboard(self, data: Dict) -> str:
        """保存看板到文件"""
        html = self.generate_html(data)
        filepath = os.path.join(self.output_dir, config.HTML_FILENAME)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath


if __name__ == "__main__":
    from data_fetcher import DataFetcher
    from indicators import process_all_assets
    
    fetcher = DataFetcher()
    raw_data = fetcher.fetch_all_assets()
    processed_data = process_all_assets(raw_data)
    
    generator = DashboardGenerator()
    filepath = generator.save_dashboard(processed_data)
    print(f"专业版看板已保存: {filepath}")
