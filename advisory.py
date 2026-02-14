"""
买入建议模块 - 多专家会诊系统
聚合趋势、均值回归、动量、基本面四维度分析
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class SignalStrength(Enum):
    STRONG_BUY = ("强烈买入", 5, "🟢🟢🟢")
    BUY = ("买入", 4, "🟢🟢")
    WEAK_BUY = ("轻仓买入", 3, "🟢")
    HOLD = ("持有观望", 2, "🟡")
    WEAK_SELL = ("考虑减仓", 1, "🟠")
    SELL = ("卖出", 0, "🔴")
    
    def __init__(self, cn_name, score, icon):
        self.cn_name = cn_name
        self.score = score
        self.icon = icon

@dataclass
class ExpertOpinion:
    """单个专家观点"""
    expert_name: str
    signal: SignalStrength
    reasoning: str
    confidence: float  # 0-1
    key_metrics: Dict[str, float]

@dataclass
class AssetRecommendation:
    """资产推荐结果"""
    symbol: str
    name: str
    category: str
    current_price: float
    
    # 五专家观点
    trend_expert: ExpertOpinion    # 趋势专家
    mean_rev_expert: ExpertOpinion  # 均值回归专家
    momentum_expert: ExpertOpinion  # 动量专家
    fundamental_expert: ExpertOpinion  # 基本面专家
    bb_cci_expert: ExpertOpinion   # BB+CCI专家（用户偏好）
    
    # 综合结果
    consensus_signal: SignalStrength
    consensus_score: float  # 0-100
    consensus_reasoning: str
    risk_level: str  # 低/中/高
    position_size: str  # 建议仓位
    stop_loss: float
    take_profit: float
    
    # 排名
    rank_in_category: int
    overall_rank: int


class AdvisoryEngine:
    """买入建议引擎"""
    
    def __init__(self):
        self.expert_weights = {
            'trend': 0.25,
            'mean_reversion': 0.25,
            'momentum': 0.25,
            'fundamental': 0.25
        }
    
    def analyze_asset(self, symbol: str, data: Dict) -> AssetRecommendation:
        """
        分析单个资产，生成四专家观点
        """
        if not data:
            return None
        
        price = data.get('current_price', 0)
        ma10 = data.get('ma_10', price)
        ma50 = data.get('ma_50', price)
        rsi = data.get('rsi', 50)
        change_1d = data.get('daily_change_pct', 0)
        change_ytd = data.get('ytd_return', 0)
        volatility = data.get('volatility', 0)
        high_52w = data.get('high_52w', price)
        low_52w = data.get('low_52w', price)
        
        # 52周位置
        week_range = high_52w - low_52w if high_52w != low_52w else 1
        week_position = ((price - low_52w) / week_range) * 100
        
        # === 用户偏好指标 ===
        ma_120 = data.get('ma_120', ma50)
        bb_upper = data.get('bb_upper', price * 1.02)
        bb_lower = data.get('bb_lower', price * 0.98)
        bb_middle = data.get('bb_middle', price)
        bb_position = data.get('bb_position', 'middle')
        bb_width = data.get('bb_width', 4)
        cci_120 = data.get('cci_120', 0)
        
        # === 专家1: 趋势专家 (加入120 SMA) ===
        trend_signal, trend_reason = self._trend_analysis(
            price, ma10, ma50, change_1d, ma_120
        )
        trend_expert = ExpertOpinion(
            expert_name="趋势专家 (Trend Following)",
            signal=trend_signal,
            reasoning=trend_reason,
            confidence=0.75 if abs(change_1d) > 2 else 0.6,
            key_metrics={"MA10": ma10, "MA50": ma50, "Price/MA50": price/ma50 if ma50 != 0 else 1.0}
        )
        
        # === 专家2: 均值回归专家 ===
        mean_rev_signal, mean_rev_reason = self._mean_reversion_analysis(
            price, ma50, rsi, week_position, change_1d
        )
        mean_rev_expert = ExpertOpinion(
            expert_name="均值回归专家 (Mean Reversion)",
            signal=mean_rev_signal,
            reasoning=mean_rev_reason,
            confidence=0.8 if rsi < 30 or rsi > 70 else 0.5,
            key_metrics={"RSI": rsi, "52W_Position": week_position, "Dist_to_MA50": (price-ma50)/ma50*100 if ma50 != 0 else 0}
        )
        
        # === 专家3: 动量专家 ===
        momentum_signal, momentum_reason = self._momentum_analysis(
            change_ytd, change_1d, rsi, volatility
        )
        momentum_expert = ExpertOpinion(
            expert_name="动量专家 (Momentum)",
            signal=momentum_signal,
            reasoning=momentum_reason,
            confidence=0.7 if abs(change_ytd) > 10 else 0.55,
            key_metrics={"YTD": change_ytd, "1D": change_1d, "RSI": rsi, "Vol": volatility}
        )
        
        # === 专家4: 价值专家 ===
        fundamental_signal, fundamental_reason = self._fundamental_analysis(
            price, ma50, rsi, week_position, volatility, symbol
        )
        fundamental_expert = ExpertOpinion(
            expert_name="价值专家 (Value)",
            signal=fundamental_signal,
            reasoning=fundamental_reason,
            confidence=0.65,
            key_metrics={"52W_Position": week_position, "Volatility": volatility}
        )
        
        # === 专家5: BB+CCI专家 (用户偏好) ===
        bb_cci_signal, bb_cci_reason = self._bb_cci_analysis(
            price, bb_upper, bb_lower, bb_middle, bb_position, bb_width, cci_120
        )
        bb_cci_expert = ExpertOpinion(
            expert_name="BB+CCI专家 (User Pref)",
            signal=bb_cci_signal,
            reasoning=bb_cci_reason,
            confidence=0.85,  # 用户偏好指标权重更高
            key_metrics={
                "BB_Position": bb_position,
                "BB_Width": f"{bb_width:.1f}%",
                "CCI_120": f"{cci_120:.1f}"
            }
        )
        
        # === 综合共识（五专家） ===
        consensus_signal, consensus_score, consensus_reason, risk_level = self._calculate_consensus(
            trend_expert, mean_rev_expert, momentum_expert, fundamental_expert, bb_cci_expert
        )
        
        # 仓位和止损建议
        position_size = self._calculate_position_size(consensus_score, risk_level, volatility)
        stop_loss = self._calculate_stop_loss(price, volatility, consensus_signal)
        take_profit = self._calculate_take_profit(price, volatility, consensus_signal)
        
        return AssetRecommendation(
            symbol=symbol,
            name=data.get('name', symbol),
            category=data.get('category', 'unknown'),
            current_price=price,
            trend_expert=trend_expert,
            mean_rev_expert=mean_rev_expert,
            momentum_expert=momentum_expert,
            fundamental_expert=fundamental_expert,
            bb_cci_expert=bb_cci_expert,
            consensus_signal=consensus_signal,
            consensus_score=consensus_score,
            consensus_reasoning=consensus_reason,
            risk_level=risk_level,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            rank_in_category=0,
            overall_rank=0
        )
    
    def _trend_analysis(self, price, ma10, ma50, change_1d, ma_120=None) -> Tuple[SignalStrength, str]:
        """趋势专家：MA金叉死叉、120 SMA趋势判断"""
        if ma50 == 0:
            return SignalStrength.HOLD, "数据不足，无法判断趋势"
        
        # 原有MA分析
        if price > ma10 > ma50 and change_1d > 0:
            signal = SignalStrength.BUY
            reason = f"多头排列，价格${price:.2f} > MA10(${ma10:.2f}) > MA50(${ma50:.2f})"
        elif price < ma10 < ma50 and change_1d < 0:
            signal = SignalStrength.SELL
            reason = f"空头排列，价格${price:.2f} < MA10(${ma10:.2f}) < MA50(${ma50:.2f})"
        elif price > ma50:
            signal = SignalStrength.WEAK_BUY
            reason = f"价格在MA50上方，中期趋势向上"
        else:
            signal = SignalStrength.HOLD
            reason = f"趋势不明朗，MA10(${ma10:.2f})与MA50(${ma50:.2f})纠缠"
        
        # 加入120 SMA分析（用户偏好）
        if ma_120 and ma_120 != 0:
            dist_120 = (price - ma_120) / ma_120 * 100
            if dist_120 > 5:
                reason += f" | 120SMA上方+{dist_120:.1f}%，强势"
            elif dist_120 < -5:
                reason += f" | 120SMA下方{dist_120:.1f}%，偏弱"
            else:
                reason += f" | 120SMA附近({dist_120:+.1f}%)"
        
        return signal, reason
    
    def _mean_reversion_analysis(self, price, ma50, rsi, week_position, change_1d) -> Tuple[SignalStrength, str]:
        """均值回归专家：RSI超买超卖、偏离均线程度"""
        dist_to_ma = (price - ma50) / ma50 * 100 if ma50 != 0 else 0
        
        if rsi < 30 and dist_to_ma < -5:
            return SignalStrength.STRONG_BUY, f"超卖区域！RSI={rsi:.1f}，偏离MA50 {dist_to_ma:.1f}%，均值回归概率高"
        elif rsi > 70 and dist_to_ma > 5:
            return SignalStrength.SELL, f"超买区域！RSI={rsi:.1f}，偏离MA50 +{dist_to_ma:.1f}%，回调风险"
        elif rsi < 40 and week_position < 30:
            return SignalStrength.BUY, f"接近超卖，RSI={rsi:.1f}，处于52周低位({week_position:.1f}%)"
        elif rsi > 60 and week_position > 70:
            return SignalStrength.WEAK_SELL, f"接近超买，RSI={rsi:.1f}，处于52周高位({week_position:.1f}%)"
        else:
            return SignalStrength.HOLD, f"RSI={rsi:.1f}中性，偏离MA50 {dist_to_ma:+.1f}%"
    
    def _momentum_analysis(self, ytd, change_1d, rsi, volatility) -> Tuple[SignalStrength, str]:
        """动量专家：YTD表现、短期动量、波动率调整"""
        if ytd > 15 and change_1d > 0 and rsi > 50:
            return SignalStrength.BUY, f"强动量！YTD +{ytd:.1f}%，今日+{change_1d:.1f}%，顺势操作"
        elif ytd < -10 and change_1d < 0:
            return SignalStrength.WEAK_SELL, f"弱势延续，YTD {ytd:.1f}%，动量向下"
        elif abs(ytd) < 5 and volatility < 15:
            return SignalStrength.WEAK_BUY, f"低波动盘整，YTD {ytd:.1f}%，等待突破"
        else:
            return SignalStrength.HOLD, f"动量中性，YTD {ytd:+.1f}%，波动率{volatility:.1f}%"
    
    def _fundamental_analysis(self, price, ma50, rsi, week_position, volatility, symbol) -> Tuple[SignalStrength, str]:
        """价值专家：52周位置、波动率评估"""
        if week_position < 25 and volatility < 20:
            return SignalStrength.BUY, f"价值区域！处于52周低位({week_position:.1f}%)，波动率低，安全边际高"
        elif week_position > 80:
            return SignalStrength.WEAK_SELL, f"估值偏高，处于52周高位({week_position:.1f}%)，注意回撤风险"
        elif week_position < 50:
            return SignalStrength.WEAK_BUY, f"低于年中值({week_position:.1f}%)，具有一定吸引力"
        else:
            return SignalStrength.HOLD, f"估值中性，处于52周{week_position:.1f}%位置"

    def _bb_cci_analysis(self, price, bb_upper, bb_lower, bb_middle, bb_position, bb_width, cci_120) -> Tuple[SignalStrength, str]:
        """
        BB+CCI专家（用户偏好指标）
        
        策略：
        - BB下轨 + CCI < -100 → 超卖买入
        - BB上轨 + CCI > 100 → 超买卖出
        - 中轨附近 + CCI中性 → 观望
        """
        # 布林带分析
        bb_pct = ((price - bb_lower) / (bb_upper - bb_lower) * 100) if (bb_upper != bb_lower) else 50
        
        # 综合信号
        # 强烈买入：BB下轨附近 + CCI超卖
        if bb_position == 'lower' and cci_120 < -100:
            return SignalStrength.STRONG_BUY, f"BB下轨({bb_pct:.0f}%) + CCI超卖({cci_120:.0f})，强烈反弹信号"
        
        # 买入：BB下轨 或 CCI超卖
        elif bb_position == 'lower' or cci_120 < -100:
            return SignalStrength.BUY, f"BB下轨{bb_pct:.0f}% 或 CCI={cci_120:.0f}，超卖区域"
        
        # 强烈卖出：BB上轨 + CCI超买
        elif bb_position == 'upper' and cci_120 > 100:
            return SignalStrength.SELL, f"BB上轨({bb_pct:.0f}%) + CCI超买({cci_120:.0f})，回调风险"
        
        # 卖出：BB上轨 或 CCI超买
        elif bb_position == 'upper' or cci_120 > 100:
            return SignalStrength.WEAK_SELL, f"BB上轨{bb_pct:.0f}% 或 CCI={cci_120:.0f}，超买区域"
        
        # 中轨附近
        elif bb_position == 'middle':
            if -50 < cci_120 < 50:
                return SignalStrength.HOLD, f"BB中轨({bb_pct:.0f}%) + CCI中性({cci_120:.0f})，震荡观望"
            elif cci_120 < -50:
                return SignalStrength.WEAK_BUY, f"BB中轨 + CCI偏弱({cci_120:.0f})，关注下轨"
            else:
                return SignalStrength.WEAK_SELL, f"BB中轨 + CCI偏强({cci_120:.0f})，关注上轨"
        
        else:
            return SignalStrength.HOLD, f"BB位置{bb_position}({bb_pct:.0f}%)，CCI={cci_120:.0f}"
    
    def _calculate_consensus(self, trend, mean_rev, momentum, fundamental, bb_cci) -> Tuple[SignalStrength, float, str, str]:
        """计算五专家共识（加入BB+CCI专家）"""
        signals = [trend.signal.score, mean_rev.signal.score, momentum.signal.score, fundamental.signal.score, bb_cci.signal.score]
        
        # BB+CCI专家权重更高（用户偏好）
        weights = [0.2, 0.2, 0.2, 0.2, 0.2]  # 平均权重，可以调整
        weighted_score = sum(s * w for s, w in zip(signals, weights))
        avg_score = weighted_score
        
        # 分歧度
        disagreement = max(signals) - min(signals)
        
        # 映射回SignalStrength
        if avg_score >= 4.5:
            consensus = SignalStrength.STRONG_BUY
        elif avg_score >= 3.5:
            consensus = SignalStrength.BUY
        elif avg_score >= 2.5:
            consensus = SignalStrength.WEAK_BUY
        elif avg_score >= 1.5:
            consensus = SignalStrength.HOLD
        elif avg_score >= 0.5:
            consensus = SignalStrength.WEAK_SELL
        else:
            consensus = SignalStrength.SELL
        
        # 共识理由
        buy_count = sum(1 for s in signals if s >= 3)
        sell_count = sum(1 for s in signals if s <= 1)
        
        if buy_count >= 3:
            reason = f"四专家中{buy_count}位建议买入，分歧度{disagreement}"
        elif sell_count >= 2:
            reason = f"四专家中{sell_count}位建议卖出/减仓"
        elif disagreement <= 1:
            reason = "四专家意见高度一致，信心度高"
        else:
            reason = f"专家意见分歧(分歧度{disagreement})，需结合宏观判断"
        
        # 风险等级
        if disagreement >= 3:
            risk = "高"
        elif disagreement >= 2:
            risk = "中"
        else:
            risk = "低"
        
        # 0-100分
        consensus_100 = (avg_score / 5) * 100
        
        return consensus, consensus_100, reason, risk
    
    def _calculate_position_size(self, score, risk, volatility) -> str:
        """计算建议仓位"""
        if score >= 80 and risk == "低":
            return "15-20%"
        elif score >= 70:
            return "10-15%"
        elif score >= 60:
            return "5-10%"
        elif score >= 40:
            return "3-5%（观察仓）"
        else:
            return "0-2%（试探性）"
    
    def _calculate_stop_loss(self, price, volatility, signal) -> float:
        """计算止损位"""
        if signal.score >= 4:  # 买入信号
            stop_pct = max(volatility * 1.5, 5)  # 波动率1.5倍或5%
        elif signal.score <= 1:  # 卖出信号
            stop_pct = max(volatility, 3)
        else:
            stop_pct = volatility * 2
        return price * (1 - stop_pct / 100)
    
    def _calculate_take_profit(self, price, volatility, signal) -> float:
        """计算止盈位"""
        if signal.score >= 4:
            tp_pct = max(volatility * 3, 10)  # 风险回报比 1:2
        else:
            tp_pct = volatility * 2
        return price * (1 + tp_pct / 100)
    
    def analyze_all(self, data: Dict) -> List[AssetRecommendation]:
        """分析所有资产，生成推荐列表"""
        recommendations = []
        
        for category, assets in data.items():
            for symbol, info in assets.items():
                if info:
                    rec = self.analyze_asset(symbol, info)
                    if rec:
                        rec.category = category
                        recommendations.append(rec)
        
        # 排序：按综合得分降序
        recommendations.sort(key=lambda x: x.consensus_score, reverse=True)
        
        # 分配总排名
        for i, rec in enumerate(recommendations):
            rec.overall_rank = i + 1
        
        # 类别内排名
        category_counts = {}
        for rec in recommendations:
            cat = rec.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        category_ranks = {}
        for rec in recommendations:
            cat = rec.category
            category_ranks[cat] = category_ranks.get(cat, 0) + 1
            rec.rank_in_category = category_ranks[cat]
        
        return recommendations
    
    def get_top_picks(self, recommendations: List[AssetRecommendation], n: int = 5) -> List[AssetRecommendation]:
        """获取前N个推荐"""
        buy_signals = [r for r in recommendations if r.consensus_score >= 60]
        return buy_signals[:n]
    
    def get_category_leaders(self, recommendations: List[AssetRecommendation]) -> Dict[str, AssetRecommendation]:
        """获取每个类别的冠军"""
        leaders = {}
        for rec in recommendations:
            if rec.rank_in_category == 1 and rec.consensus_score >= 60:
                leaders[rec.category] = rec
        return leaders


if __name__ == "__main__":
    # 测试
    engine = AdvisoryEngine()
    
    test_data = {
        'AAPL': {
            'current_price': 175.0,
            'ma_10': 170.0,
            'ma_50': 165.0,
            'rsi': 45,
            'daily_change_pct': 2.5,
            'ytd_return': 12.0,
            'volatility': 18.0,
            'high_52w': 200.0,
            'low_52w': 150.0,
            'name': 'Apple Inc.'
        }
    }
    
    rec = engine.analyze_asset('AAPL', test_data['AAPL'])
    print(f"\n{'='*60}")
    print(f"资产: {rec.symbol} ({rec.name})")
    print(f"当前价格: ${rec.current_price:.2f}")
    print(f"{'='*60}")
    print(f"\n【趋势专家】{rec.trend_expert.signal.cn_name}")
    print(f"  理由: {rec.trend_expert.reasoning}")
    print(f"\n【均值回归专家】{rec.mean_rev_expert.signal.cn_name}")
    print(f"  理由: {rec.mean_rev_expert.reasoning}")
    print(f"\n【动量专家】{rec.momentum_expert.signal.cn_name}")
    print(f"  理由: {rec.momentum_expert.reasoning}")
    print(f"\n【价值专家】{rec.fundamental_expert.signal.cn_name}")
    print(f"  理由: {rec.fundamental_expert.reasoning}")
    print(f"\n{'='*60}")
    print(f"【🏆 综合建议】{rec.consensus_signal.icon} {rec.consensus_signal.cn_name}")
    print(f"  综合得分: {rec.consensus_score:.1f}/100")
    print(f"  共识理由: {rec.consensus_reasoning}")
    print(f"  风险等级: {rec.risk_level}")
    print(f"  建议仓位: {rec.position_size}")
    print(f"  止损位: ${rec.stop_loss:.2f}")
    print(f"  止盈位: ${rec.take_profit:.2f}")
    print(f"{'='*60}")
