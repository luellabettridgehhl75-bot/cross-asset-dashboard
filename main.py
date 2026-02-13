"""
主程序入口 - 跨资产实时监控系统
"""

import os
import sys
import time
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import DataFetcher
from indicators import process_all_assets
from dashboard import DashboardGenerator
from telegram_bot import TelegramBot
import config


def main(send_telegram: bool = False):
    """
    主函数
    
    Args:
        send_telegram: 是否发送Telegram通知
    """
    print("=" * 60)
    print("📊 跨资产实时监控系统")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 抓取数据
    print("\n🔍 正在抓取数据...")
    fetcher = DataFetcher()
    raw_data = fetcher.fetch_all_assets()
    
    # 2. 计算指标
    print("\n📐 正在计算技术指标...")
    processed_data = process_all_assets(raw_data)
    
    # 3. 生成看板
    print("\n🎨 正在生成HTML看板...")
    generator = DashboardGenerator()
    dashboard_path = generator.save_dashboard(processed_data)
    print(f"✅ 看板已保存: {dashboard_path}")
    
    # 4. 发送Telegram通知（可选）
    if send_telegram:
        print("\n📱 正在发送Telegram通知...")
        bot = TelegramBot()
        bot.send_summary(processed_data)
    
    # 5. 打印摘要
    print("\n" + "=" * 60)
    print("📈 监控摘要")
    print("=" * 60)
    
    for category, assets in processed_data.items():
        if not assets:
            continue
        
        category_name = config.CATEGORY_NAMES.get(category, category)
        print(f"\n{category_name}:")
        
        for symbol, info in assets.items():
            if not info:
                continue
            
            price = info.get('current_price', 0)
            change = info.get('daily_change_pct', 0)
            trend = info.get('trend', '🟡')
            
            print(f"  {trend} {symbol}: ${price:.2f} ({change:+.2f}%)")
    
    print("\n" + "=" * 60)
    print(f"✅ 完成! 看板文件: {dashboard_path}")
    print("=" * 60)
    
    return dashboard_path


def run_scheduled():
    """定时运行模式"""
    import schedule
    
    def job():
        try:
            main(send_telegram=True)
        except Exception as e:
            print(f"Error in scheduled job: {e}")
    
    # 每小时运行一次
    schedule.every().hour.do(job)
    
    print("⏰ 定时模式已启动，每小时运行一次...")
    print("按 Ctrl+C 停止")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n👋 已停止")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='跨资产实时监控系统')
    parser.add_argument('--telegram', '-t', action='store_true', 
                        help='发送Telegram通知')
    parser.add_argument('--schedule', '-s', action='store_true',
                        help='定时运行模式')
    
    args = parser.parse_args()
    
    if args.schedule:
        run_scheduled()
    else:
        main(send_telegram=args.telegram)
