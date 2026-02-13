"""
技术指标计算模块
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime
import config


class IndicatorCalculator:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int) -> pd.Series:
        """计算简单移动平均线"""
        return df['Close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """计算指数移动平均线"""
        return df['Close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_returns(df: pd.DataFrame, periods: int = 1) -> pd.Series:
        """计算收益率"""
        return df['Close'].pct_change(periods=periods) * 100
    
    @staticmethod
    def calculate_ytd_return(df: pd.DataFrame) -> float:
        """计算年内收益率 (从2025-12-31到现在)"""
        try:
            # 获取2025年底的价格
            year_end_2025 = df[df.index <= '2025-12-31']
            if len(year_end_2025) > 0:
                year_end_price = year_end_2025['Close'].iloc[-1]
            else:
                # 如果没有2025年底数据，使用最早可用数据
                year_end_price = df['Close'].iloc[0]
            
            current_price = df['Close'].iloc[-1]
            return ((current_price - year_end_price) / year_end_price) * 100
        except Exception as e:
            print(f"Error calculating YTD return: {e}")
            return 0.0
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame, period: int = 20) -> float:
        """计算波动率（标准差）"""
        returns = df['Close'].pct_change().dropna()
        return returns.tail(period).std() * 100
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> float:
        """计算RSI相对强弱指标"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    @staticmethod
    def determine_trend(df: pd.DataFrame) -> Tuple[str, str]:
        """
        判断趋势
        
        Returns:
            (趋势标签, 趋势颜色)
            趋势: 🟢上涨 / 🔴下跌 / 🟡震荡
        """
        if len(df) < config.MA_LONG:
            return "🟡震荡", "neutral"
        
        # 计算均线
        ma_short = IndicatorCalculator.calculate_ma(df, config.MA_SHORT)
        ma_long = IndicatorCalculator.calculate_ma(df, config.MA_LONG)
        
        current_price = df['Close'].iloc[-1]
        current_ma_short = ma_short.iloc[-1]
        current_ma_long = ma_long.iloc[-1]
        
        # 计算近期波动
        recent_returns = df['Close'].pct_change(5).iloc[-1]
        
        # 趋势判断逻辑
        if current_price > current_ma_short > current_ma_long and recent_returns > 0.01:
            return "🟢上涨", "bullish"
        elif current_price < current_ma_short < current_ma_long and recent_returns < -0.01:
            return "🔴下跌", "bearish"
        else:
            return "🟡震荡", "neutral"
    
    @staticmethod
    def calculate_relative_strength(df: pd.DataFrame, benchmark_df: Optional[pd.DataFrame] = None) -> str:
        """
        计算相对强弱
        
        Returns:
            相对强弱评级 (Strong / Moderate / Weak)
        """
        # 计算近20日收益率
        if len(df) >= 20:
            returns_20d = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100
        else:
            returns_20d = 0
        
        # 简单的强弱判断
        if returns_20d > 5:
            return "Strong 💪"
        elif returns_20d > 0:
            return "Moderate 👍"
        elif returns_20d > -5:
            return "Weak 👎"
        else:
            return "Very Weak ❌"
    
    @classmethod
    def calculate_all_indicators(cls, df: pd.DataFrame, category: str = "") -> Dict:
        """
        计算所有技术指标
        
        Args:
            df: 价格数据DataFrame
            category: 资产类别
            
        Returns:
            包含所有指标的字典
        """
        if df is None or df.empty or len(df) < 2:
            return {}
        
        # 基础价格数据
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        
        # 24小时/日涨跌幅
        daily_change_pct = ((current_price - prev_price) / prev_price) * 100
        daily_change = current_price - prev_price
        
        # 移动平均线
        ma_10 = cls.calculate_ma(df, 10).iloc[-1] if len(df) >= 10 else current_price
        ma_50 = cls.calculate_ma(df, 50).iloc[-1] if len(df) >= 50 else current_price
        
        # 年内收益率
        ytd_return = cls.calculate_ytd_return(df)
        
        # 趋势判断
        trend, trend_color = cls.determine_trend(df)
        
        # 相对强弱
        rel_strength = cls.calculate_relative_strength(df)
        
        # RSI
        rsi = cls.calculate_rsi(df)
        
        # 波动率
        volatility = cls.calculate_volatility(df)
        
        # 52周高低点
        high_52w = df['High'].tail(252).max() if len(df) >= 252 else df['High'].max()
        low_52w = df['Low'].tail(252).min() if len(df) >= 252 else df['Low'].min()
        
        return {
            'current_price': current_price,
            'prev_price': prev_price,
            'daily_change': daily_change,
            'daily_change_pct': daily_change_pct,
            'ma_10': ma_10,
            'ma_50': ma_50,
            'ytd_return': ytd_return,
            'trend': trend,
            'trend_color': trend_color,
            'relative_strength': rel_strength,
            'rsi': rsi,
            'volatility': volatility,
            'high_52w': high_52w,
            'low_52w': low_52w,
        }


def process_all_assets(fetcher_data: Dict) -> Dict:
    """
    处理所有资产数据并计算指标
    
    Args:
        fetcher_data: 从DataFetcher获取的数据
        
    Returns:
        包含指标的数据字典
    """
    calculator = IndicatorCalculator()
    results = {}
    
    for category, assets in fetcher_data.items():
        category_results = {}
        
        for symbol, data in assets.items():
            df = data['data']
            indicators = calculator.calculate_all_indicators(df, category)
            
            category_results[symbol] = {
                'name': data['name'],
                **indicators
            }
        
        results[category] = category_results
    
    return results


if __name__ == "__main__":
    # 测试指标计算
    from data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    data = fetcher.fetch_all_assets()
    results = process_all_assets(data)
    
    for category, assets in results.items():
        print(f"\n{category}:")
        for symbol, info in assets.items():
            print(f"  {symbol}: ${info['current_price']:.2f} ({info['daily_change_pct']:+.2f}%) {info['trend']}")
