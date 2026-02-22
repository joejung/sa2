import asyncio
import logging
from datetime import datetime
from sqlalchemy import func
from PyQt6.QtCore import QObject, pyqtSignal
from sahelper.database.session import SessionLocal
from sahelper.database.models import Trade, StockData

logger = logging.getLogger(__name__)

class AttributionService(QObject):
    """Calculates contribution of each trade/holding to overall P&L."""
    attribution_ready = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    async def calculate_attribution(self):
        """Analyze trades and current prices to attribute gains/losses."""
        logger.info("Calculating performance attribution...")
        await asyncio.sleep(0.5)
        
        with SessionLocal() as session:
            # Group trades by ticker
            tickers = session.query(Trade.ticker).distinct().all()
            results = []
            
            total_realized_pl = 0
            total_unrealized_pl = 0
            
            for (symbol,) in tickers:
                trades = session.query(Trade).filter_by(ticker=symbol).all()
                stock = session.query(StockData).filter_by(ticker=symbol).first()
                
                # Simple attribution logic
                total_qty = sum(t.quantity for t in trades)
                
                # Realized P&L (very simplified for this demo)
                realized_pl = 0
                buy_cost = 0
                buy_qty = 0
                for t in trades:
                    if t.quantity > 0:
                        buy_cost += t.quantity * t.price
                        buy_qty += t.quantity
                    else:
                        # Realized gain on sale
                        if buy_qty > 0:
                            avg_buy_price = buy_cost / buy_qty
                            realized_pl += abs(t.quantity) * (t.price - avg_buy_price)
                
                # Unrealized P&L
                unrealized_pl = 0
                if stock and total_qty > 0:
                    avg_cost = buy_cost / buy_qty if buy_qty > 0 else 0
                    unrealized_pl = total_qty * (stock.last_price - avg_cost)
                
                results.append({
                    "ticker": symbol,
                    "realized_pl": realized_pl,
                    "unrealized_pl": unrealized_pl,
                    "total_contribution": realized_pl + unrealized_pl
                })
            
            # Sort by total contribution
            results.sort(key=lambda x: x["total_contribution"], reverse=True)
            self.attribution_ready.emit(results)

    def record_trade(self, ticker, qty, price):
        """Helper to add a trade manually for demo purposes."""
        with SessionLocal() as session:
            trade = Trade(ticker=ticker, quantity=qty, price=price)
            session.add(trade)
            session.commit()
            logger.info(f"Recorded trade: {ticker} {qty} @ {price}")
