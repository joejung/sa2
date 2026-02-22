import asyncio
import logging
import numpy as np
import pandas as pd
import yfinance as yf
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class RiskService(QObject):
    """Calculates portfolio risk metrics (Beta, Sharpe, Drawdown)."""
    metrics_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    async def calculate_risk(self, holdings):
        """
        holdings: list of dicts {'ticker': str, 'value': float}
        """
        if not holdings:
            return

        try:
            loop = asyncio.get_event_loop()
            
            # 1. Prepare Data
            # Map ticker -> weight
            portfolio_map = {h['ticker']: h['value'] for h in holdings}
            tickers = list(portfolio_map.keys())
            
            # Add Benchmark (SPY)
            all_tickers = list(set(tickers + ['SPY']))
            
            # 2. Fetch History (1 Year)
            # Use 'threads=True' for parallel download
            # auto_adjust=True handles splits/dividends for Total Return
            df = await loop.run_in_executor(None, lambda: yf.download(all_tickers, period="1y", progress=False, auto_adjust=True)['Close'])
            
            if df.empty:
                raise ValueError("No data fetched")
            
            # Returns
            returns = df.pct_change().dropna()
            
            # 3. Calculate Portfolio Returns
            # We need to construct a weighted return series
            # Create a weights series aligned with the DataFrame columns
            
            # Filter only assets in our portfolio (exclude SPY if not in portfolio)
            asset_cols = [c for c in returns.columns if c in portfolio_map]
            
            if not asset_cols:
                return

            # Extract weights for the available columns
            total_value = sum(portfolio_map.values())
            if total_value == 0: return
            
            # Align weights to the sorted columns from yfinance
            weights = np.array([portfolio_map[c] for c in asset_cols])
            weights = weights / total_value
            
            # Calculate weighted returns
            # asset_cols ensures we only take the columns we have weights for
            asset_returns = returns[asset_cols]
            
            # Dot product: (Rows x Cols) . (Cols x 1) -> (Rows x 1)
            port_returns = asset_returns.dot(weights)
            
            # Benchmark Returns
            spy_returns = returns['SPY'] if 'SPY' in returns.columns else returns.iloc[:, 0] # Fallback
            
            # 4. Calculate Metrics
            # Align dates (intersection)
            combined = pd.concat([port_returns, spy_returns], axis=1).dropna()
            p_ret = combined.iloc[:, 0]
            m_ret = combined.iloc[:, 1]
            
            # Beta
            covariance = np.cov(p_ret, m_ret)[0][1]
            variance = np.var(m_ret)
            beta = covariance / variance if variance != 0 else 0
            
            # Sharpe Ratio (Risk Free Rate assumed 4% -> 0.04/252 daily)
            rf_daily = 0.04 / 252
            excess_returns = p_ret - rf_daily
            std_dev = p_ret.std()
            sharpe = (excess_returns.mean() / std_dev) * np.sqrt(252) if std_dev != 0 else 0
            
            # Max Drawdown
            cum_returns = (1 + p_ret).cumprod()
            peak = cum_returns.cummax()
            drawdown = (cum_returns - peak) / peak
            max_drawdown = drawdown.min()
            
            # Volatility (Annualized)
            volatility = std_dev * np.sqrt(252)

            metrics = {
                "Beta": f"{beta:.2f}",
                "Sharpe Ratio": f"{sharpe:.2f}",
                "Max Drawdown": f"{max_drawdown*100:.2f}%",
                "Volatility": f"{volatility*100:.2f}%",
                "Total Value": f"${total_value:,.2f}"
            }
            
            self.metrics_ready.emit(metrics)

        except Exception as e:
            logger.error(f"Risk calculation failed: {e}")
            self.error_occurred.emit(str(e))
