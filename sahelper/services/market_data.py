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
            {"name": "S&P 500", "ticker": "SPY"},
            {"name": "Nasdaq 100", "ticker": "QQQ"},
            {"name": "Russell 2000", "ticker": "IWM"},
            {"name": "Volatility", "ticker": "^VIX"},
            {"name": "US 10Y Yield", "ticker": "^TNX"},
            {"name": "DXY Index", "ticker": "DX-Y.NYB"}
        ]
        self.cache = {} # Store last known good data

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
        
        # Sort by latest (yfinance news usually comes in order, but we aggregate)
        # We don't have timestamps easily but we can just emit what we have
        self.news_updated.emit(news_aggregated[:15]) # Return top 15

    async def run_live_feed(self):
        """Infinite loop fetching real data."""
        # 1. Initial Population
        logger.info("Initializing market data feed...")
        await self.fetch_global_news() # Initial news
        """Fetch 1 month of history for sparklines."""
        try:
            loop = asyncio.get_event_loop()
            # Run blocking yfinance call in a thread
            ticker = await loop.run_in_executor(None, yf.Ticker, ticker_symbol)
            hist = await loop.run_in_executor(None, lambda: ticker.history(period="1mo", interval="1d"))
            
            if hist.empty:
                return []
            
            # Return list of closing prices
            return hist['Close'].tolist()
        except Exception as e:
            logger.error(f"Failed to fetch history for {ticker_symbol}: {e}")
            return []

    async def get_latest_price(self, ticker_symbol):
        """Fetch the absolute latest price."""
        try:
            loop = asyncio.get_event_loop()
            # fast_info is often faster/more reliable for current price than history
            ticker = await loop.run_in_executor(None, yf.Ticker, ticker_symbol)
            # Try fast_info first, fallback to history
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
        # 1. Initial Population
        logger.info("Initializing market data feed...")
        for t in self.tickers:
            history = await self.fetch_history(t["ticker"])
            price, change_pct = await self.get_latest_price(t["ticker"])
            
            if price is None and history:
                price = history[-1]
                change_pct = 0.0
            elif price is None:
                price = 100.0 # Fallback
                change_pct = 0.0

            self.cache[t["ticker"]] = {
                "name": t["name"],
                "ticker": t["ticker"],
                "value": price,
                "change_pct": change_pct,
                "history": history
            }

        iteration = 0
        while True:
            # Refresh news every 20 iterations (approx 5 mins if 15s sleep)
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
                    # Append to history for live feel (optional, simplistic)
                    # For a sparkline, we might just want to update the last point or append if it's a new day.
                    # For simplicity, we just keep the history as is or append the live price.
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
            await asyncio.sleep(15) # Poll every 15s to respect API limits
