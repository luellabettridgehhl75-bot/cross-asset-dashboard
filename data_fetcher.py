"""
数据抓取模块 - 从Yahoo Finance和Binance获取数据
"""

import yfinance as yf
import pandas as pd
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
import config


class DataFetcher:
    """数据抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        
    def fetch_yahoo_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        从Yahoo Finance获取数据
        
        Args:
            symbol: 股票代码
            period: 时间周期
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def fetch_crypto_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        从Yahoo Finance获取加密货币数据 (加密货币也使用yfinance)
        
        Args:
            symbol: 交易对 (如 BTC-USD)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1y", interval="1d")
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"Error fetching crypto {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """获取当前价格"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            # 尝试不同的价格字段
            price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            return price
        except Exception as e:
            print(f"Error getting current price for {symbol}: {e}")
            return None
    
    def fetch_all_assets(self) -> Dict[str, Dict]:
        """
        获取所有资产数据
        
        Returns:
            按类别组织的数据字典
        """
        results = {}
        
        for category, assets in config.ALL_ASSETS.items():
            print(f"Fetching {category}...")
            category_data = {}
            
            for symbol, name in assets.items():
                print(f"  - {symbol}")
                
                # 获取历史数据用于计算指标
                if category == 'crypto':
                    df = self.fetch_crypto_data(symbol)
                else:
                    # 处理宏观指标符号
                    if symbol.startswith('^'):
                        df = self.fetch_yahoo_data(symbol)
                    else:
                        df = self.fetch_yahoo_data(symbol)
                
                if df is not None and not df.empty:
                    category_data[symbol] = {
                        'name': name,
                        'data': df,
                        'current_price': df['Close'].iloc[-1],
                        'prev_close': df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1],
                    }
                else:
                    print(f"    Warning: No data for {symbol}")
            
            results[category] = category_data
        
        return results


if __name__ == "__main__":
    # 测试数据抓取
    fetcher = DataFetcher()
    data = fetcher.fetch_all_assets()
    
    for category, assets in data.items():
        print(f"\n{category}:")
        for symbol, info in assets.items():
            print(f"  {symbol}: ${info['current_price']:.2f}")
