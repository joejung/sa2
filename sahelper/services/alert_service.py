import asyncio
import logging
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

class AlertService(QObject):
    """Background service for monitoring price alerts."""
    alert_triggered = pyqtSignal(str, str, float) # (ticker, condition, current_price)

    def __init__(self, market_service):
        super().__init__()
        self.market_service = market_service
        self.alerts = [] # list of dicts: {'ticker': 'AAPL', 'condition': '>', 'value': 200.0}
        
        # Monitor the market data feed
        self.market_service.data_updated.connect(self.check_alerts)

    def add_alert(self, ticker, condition, value):
        self.alerts.append({
            'ticker': ticker,
            'condition': condition,
            'value': float(value),
            'triggered': False
        })
        logger.info(f"Alert added: {ticker} {condition} {value}")

    def check_alerts(self, data):
        """Check live data against active alerts."""
        for item in data:
            ticker = item['ticker']
            # strip formatting from value if it's a string
            try:
                current_price = float(item['value'].replace(',', ''))
            except:
                continue

            for alert in self.alerts:
                if alert['ticker'] == ticker and not alert['triggered']:
                    triggered = False
                    if alert['condition'] == '>' and current_price > alert['value']:
                        triggered = True
                    elif alert['condition'] == '<' and current_price < alert['value']:
                        triggered = True
                    
                    if triggered:
                        alert['triggered'] = True
                        self.alert_triggered.emit(ticker, alert['condition'], current_price)
