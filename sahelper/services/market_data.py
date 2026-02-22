import asyncio
import logging
import random
import yfinance as yf
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class MarketDataService(QObject):
    """Institutional Market Data Feed (Powered by yfinance)."""
    data_updated = pyqtSignal(list)
    news_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.analyzer = SentimentIntensityAnalyzer()
        self.tickers = [
            {"name": "S&P 500", "ticker": "SPY", "history": [100.0 + random.uniform(-1, 1) for _ in range(50)]},
            {"name": "Nasdaq 100", "ticker": "QQQ", "history": [100.0 + random.uniform(-1, 1) for _ in range(50)]},
            {"name": "Russell 2000", "ticker": "IWM", "history": [100.0 + random.uniform(-1, 1) for _ in range(50)]},
            {"name": "Volatility", "ticker": "^VIX", "history": [100.0 + random.uniform(-1, 1) for _ in range(50)]},
            {"name": "US 10Y Yield", "ticker": "^TNX", "history": [100.0 + random.uniform(-1, 1) for _ in range(50)]},
            {"name": "DXY Index", "ticker": "DX-Y.NYB", "history": [100.0 + random.uniform(-1, 1) for _ in range(50)]}
        ]
        self.cache = {} # Store last known good data
        for t in self.tickers:
            self.cache[t["ticker"]] = {
                "name": t["name"],
                "ticker": t["ticker"],
                "value": t["history"][-1],
                "change_pct": 0.0,
                "history": list(t["history"])
            }

    async def fetch_global_news(self):
        """Fetch news from major indices and aggregate."""
        news_aggregated = []
        seen_titles = set()
        
        loop = asyncio.get_event_loop()
        for symbol in ["SPY", "QQQ", "DIA"]:
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                news = ticker.news
                if news:
                    for item in news:
                        title = item.get("title", "")
                        if title in seen_titles: continue
                        seen_titles.add(title)
                        
                        vs = self.analyzer.polarity_scores(title)
                        sentiment = "Neutral"
                        if vs['compound'] >= 0.05: sentiment = "Bullish"
                        elif vs['compound'] <= -0.05: sentiment = "Bearish"
                        
                        news_aggregated.append({
                            "title": title,
                            "publisher": item.get("publisher"),
                            "link": item.get("link"),
                            "sentiment": sentiment,
                            "score": vs['compound']
                        })
            except Exception as e:
                logger.error(f"Failed to fetch news for {symbol}: {e}")
        
        self.news_updated.emit(news_aggregated[:15])

    async def fetch_history(self, ticker_symbol):
        """Fetch 1 month of history for sparklines."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, ticker_symbol)
            hist = await loop.run_in_executor(None, lambda: ticker.history(period="1mo", interval="1d"))
            
            if hist.empty:
                return []
            
            return hist['Close'].tolist()
        except Exception as e:
            logger.error(f"Failed to fetch history for {ticker_symbol}: {e}")
            return []

    async def get_latest_price(self, ticker_symbol):
        """Fetch the absolute latest price."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, ticker_symbol)
            info = ticker.fast_info
            price = info.last_price
            prev_close = info.previous_close
            
            change_pct = ((price - prev_close) / prev_close) if prev_close else 0.0
            
            return price, change_pct
        except Exception as e:
            logger.error(f"Failed to fetch price for {ticker_symbol}: {e}")
            return None, None

    async def run_live_feed(self):
        """Infinite loop fetching real data."""
        logger.info("Initializing market data feed...")
        await self.fetch_global_news() # Initial news
        
        # Initial Population from YFinance
        for t in self.tickers:
            symbol = t["ticker"]
            history = await self.fetch_history(symbol)
            price, change_pct = await self.get_latest_price(symbol)
            
            if price is None and history:
                price = history[-1]
                change_pct = 0.0
            elif price is None:
                price = self.cache[symbol]["value"]
                change_pct = 0.0

            if history:
                self.cache[symbol]["history"] = history
            
            self.cache[symbol]["value"] = price
            self.cache[symbol]["change_pct"] = change_pct

        iteration = 0
        while True:
            if iteration % 20 == 0 and iteration > 0:
                asyncio.create_task(self.fetch_global_news())
            
            updated_data = []
            for t in self.tickers:
                symbol = t["ticker"]
                cached = self.cache.get(symbol)
                
                # Fetch fresh data
                price, change_pct = await self.get_latest_price(symbol)
                
                if price is not None:
                    cached["value"] = price
                    cached["change_pct"] = change_pct
                    if cached["history"] and price != cached["history"][-1]:
                         cached["history"].append(price)
                         if len(cached["history"]) > 100: cached["history"].pop(0)

                updated_data.append({
                    "name": cached["name"],
                    "ticker": cached["ticker"],
                    "value": f"{cached['value']:,.2f}",
                    "change": f"{cached['change_pct']:+.2f}%",
                    "history": cached["history"]
                })
            
            self.data_updated.emit(updated_data)
            await asyncio.sleep(15) 
            iteration += 1
