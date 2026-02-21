import asyncio
import logging
import random
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class MarketDataService(QObject):
    """Institutional Market Data Feed (Simulated for high-density testing)."""
    data_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.tickers = [
            {"name": "S&P 500", "ticker": "SPY", "base": 5000, "history": []},
            {"name": "Nasdaq 100", "ticker": "QQQ", "base": 17000, "history": []},
            {"name": "Russell 2000", "ticker": "IWM", "base": 2000, "history": []},
            {"name": "Volatility", "ticker": "VIX", "base": 14, "history": []},
            {"name": "US 10Y Yield", "ticker": "TNX", "base": 4.25, "history": []},
            {"name": "DXY Index", "ticker": "DXY", "base": 104, "history": []}
        ]
        # Pre-populate history with dummy data
        for t in self.tickers:
            for _ in range(50):
                change_pct = (random.random() - 0.5) * 0.01
                t["base"] *= (1 + change_pct)
                t["history"].append(t["base"])

    async def run_live_feed(self):
        """Infinite loop simulating a live ticker feed."""
        while True:
            updated_data = []
            for t in self.tickers:
                # Add professional-level random variance (volatility)
                change_pct = (random.random() - 0.5) * 0.002 # 0.1% max variance
                current_val = t["base"] * (1 + change_pct)
                t["base"] = current_val
                
                # Append to history, keep last 100 points
                t["history"].append(current_val)
                if len(t["history"]) > 100:
                    t["history"].pop(0)

                updated_data.append({
                    "name": t["name"],
                    "ticker": t["ticker"],
                    "value": f"{current_val:,.2f}",
                    "change": f"{change_pct:+.2f}%",
                    "history": t["history"][:]
                })
            
            self.data_updated.emit(updated_data)
            await asyncio.sleep(2) # 2s update interval for Terminal feel
