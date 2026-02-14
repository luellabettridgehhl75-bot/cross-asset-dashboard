"""
Telegram推送模块 - 发送监控摘要到Telegram
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional
import config


class TelegramBot:
    """Telegram机器人"""
    
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, message: str) -> bool:
        """
        发送文本消息
        
        Args:
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        if not self.token or not self.chat_id:
            print("Telegram bot not configured. Skipping notification.")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("Telegram notification sent successfully.")
                return True
            else:
                print(f"Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_summary(self, data: Dict, recommendations: Optional[List] = None) -> bool:
        """
        发送监控摘要
        
        Args:
            data: 资产数据
            recommendations: 买入推荐列表
            
        Returns:
            是否发送成功
        """
        message = self._format_summary(data, recommendations)
        return self.send_message(message)
    
    def _format_summary(self, data: Dict, recommendations: Optional[List] = None) -> str:
        """格式化摘要消息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        message = f"""📊 *跨资产监控摘要*
⏰ {timestamp}

"""
        
        # 添加四专家推荐（如果有）
        if recommendations:
            buy_recs = [r for r in recommendations if r.consensus_score >= 60][:3]
            if buy_recs:
                message += "🏆 *四专家推荐买入*\n"
                for rec in buy_recs:
                    emoji = "🟢" if rec.consensus_score >= 75 else "🟡"
                    message += f"{emoji} #{rec.overall_rank} {rec.symbol}: {rec.consensus_signal.cn_name} ({rec.consensus_score:.0f}分)\n"
                    message += f"   建议: {rec.position_size}仓位 | 止损${rec.stop_loss:.0f}\n"
                message += "\n"
        
        # 显示每个类别的关键资产
        for category, assets in data.items():
            if not assets:
                continue
            
            category_name = config.CATEGORY_NAMES.get(category, category)
            message += f"*{category_name}*\n"
            
            # 只显示前3个资产
            for i, (symbol, info) in enumerate(assets.items()):
                if i >= 3:
                    break
                if not info:
                    continue
                
                price = info.get('current_price', 0)
                change = info.get('daily_change_pct', 0)
                trend = info.get('trend', '🟡')
                
                change_str = f"{change:+.2f}%"
                message += f"{trend} {symbol}: ${price:.2f} ({change_str})\n"
            
            message += "\n"
        
        message += "📈 [查看完整看板](https://luellabettridgehhl75-bot.github.io/cross-asset-dashboard/)"
        
        return message


if __name__ == "__main__":
    # 测试Telegram推送
    bot = TelegramBot()
    
    test_data = {
        'us_stocks': {
            'AAPL': {'current_price': 175.5, 'daily_change_pct': 1.2, 'trend': '🟢上涨'},
            'NVDA': {'current_price': 480.2, 'daily_change_pct': 2.5, 'trend': '🟢上涨'},
        }
    }
    
    bot.send_summary(test_data)
