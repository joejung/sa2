import asyncio
import logging
import yfinance as yf
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class AnalysisService(QObject):
    """Service for deep stock analysis (Charts, Fundamentals, News)."""
    # Signals
    chart_data_ready = pyqtSignal(list, list) # (ohlc_data, dates)
    indicators_ready = pyqtSignal(dict) # { 'SMA20': [], 'SMA50': [], ... }
    fundamentals_ready = pyqtSignal(dict)
    news_ready = pyqtSignal(list) # List of dicts with sentiment
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.analyzer = SentimentIntensityAnalyzer()

    async def fetch_analysis_data(self, ticker_symbol):
        """Fetch all data for a ticker."""
        if not ticker_symbol:
            return

        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, ticker_symbol)
            
            # 1. Fetch History (1 Year)
            hist = await loop.run_in_executor(None, lambda: ticker.history(period="1y"))
            
            if not hist.empty:
                # Prepare data for CandlestickItem: (t, open, close, low, high)
                ohlc_data = []
                dates = []
                for i, (idx, row) in enumerate(hist.iterrows()):
                    ohlc_data.append((i, row['Open'], row['Close'], row['Low'], row['High']))
                    dates.append(idx.strftime('%Y-%m-%d'))
                
                self.chart_data_ready.emit(ohlc_data, dates)

                # Calculate Indicators
                indicators = {
                    "SMA20": hist['Close'].rolling(window=20).mean().tolist(),
                    "SMA50": hist['Close'].rolling(window=50).mean().tolist(),
                    "SMA200": hist['Close'].rolling(window=200).mean().tolist()
                }
                self.indicators_ready.emit(indicators)
            
            # 2. Fetch Fundamentals
            info = ticker.info
            fundamentals = {
                "Market Cap": self._format_large_number(info.get("marketCap")),
                "P/E Ratio": f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A",
                "Div Yield": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A",
                "EPS": f"{info.get('trailingEps', 0):.2f}" if info.get('trailingEps') else "N/A",
                "52W High": f"${info.get('fiftyTwoWeekHigh', 0):.2f}",
                "52W Low": f"${info.get('fiftyTwoWeekLow', 0):.2f}",
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Beta": f"{info.get('beta', 0):.2f}"
            }
            self.fundamentals_ready.emit(fundamentals)

            # 3. Fetch News with Sentiment
            news = ticker.news
            formatted_news = []
            if news:
                for item in news:
                    title = item.get("title", "")
                    vs = self.analyzer.polarity_scores(title)
                    sentiment = "Neutral"
                    if vs['compound'] >= 0.05: sentiment = "Bullish"
                    elif vs['compound'] <= -0.05: sentiment = "Bearish"

                    formatted_news.append({
                        "title": title,
                        "publisher": item.get("publisher"),
                        "link": item.get("link"),
                        "type": item.get("type", "STORY"),
                        "sentiment": sentiment,
                        "sentiment_score": vs['compound']
                    })
            self.news_ready.emit(formatted_news)

        except Exception as e:
            logger.error(f"Error analyzing {ticker_symbol}: {e}")
            self.error_occurred.emit(str(e))

    def _format_large_number(self, num):
        if not num: return "N/A"
        if num >= 1e12: return f"{num/1e12:.2f}T"
        if num >= 1e9: return f"{num/1e9:.2f}B"
        if num >= 1e6: return f"{num/1e6:.2f}M"
        return str(num)
